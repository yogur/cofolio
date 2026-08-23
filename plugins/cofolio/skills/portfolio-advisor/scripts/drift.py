#!/usr/bin/env python3
"""
drift.py — Portfolio drift analysis and rebalancing calculator.

Reads portfolio.json for target weights and accepts current weights as input.
Computes drift per position and flags positions exceeding a configurable threshold.
Calculates the trades (buys/sells) needed to rebalance back to targets.

Usage:
    python drift.py [portfolio.json] [--current WEIGHTS_JSON] [--threshold PCT]
                    [--value AMOUNT] [--json]

Arguments:
    portfolio.json   Path to portfolio JSON file (default: portfolio.json)
    --current FILE   JSON file with current weights.
                     Accepts an array: [{"ticker": "SXR8", "current_weight_pct": 52.5}, ...]
                     or an object:     {"SXR8": 52.5, ...}
                     If omitted, reads current_weight_pct from each position in portfolio.json.
    --threshold PCT  Drift threshold to flag positions in percentage points (default: 5.0)
    --value AMOUNT   Current portfolio value in portfolio currency (enables trade sizing)
    --json           Output as JSON object (for skill consumption)
"""

import argparse
import json
import sys
from pathlib import Path


def load_portfolio(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    with p.open() as f:
        return json.load(f)


def load_current_weights(path: str) -> dict[str, float]:
    """
    Load current weights from a JSON file.
    Returns a mapping of {ticker_or_name: current_weight_pct}.
    Accepts either an array of objects or a plain {key: value} mapping.
    """
    p = Path(path)
    if not p.exists():
        print(f"Error: current weights file '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    with p.open() as f:
        data = json.load(f)

    result: dict[str, float] = {}
    if isinstance(data, list):
        for item in data:
            key = item.get("ticker") or item.get("name")
            if key:
                result[key] = float(item.get("current_weight_pct", 0.0))
    elif isinstance(data, dict):
        result = {k: float(v) for k, v in data.items()}
    else:
        print("Error: current weights file must be a JSON array or object.", file=sys.stderr)
        sys.exit(1)
    return result


def compute_drift(
    portfolio: dict,
    current_weights_map: dict[str, float] | None,
    threshold: float,
    portfolio_value: float | None,
) -> list[dict]:
    """
    Returns a list of per-position drift dicts, sorted by abs(drift) descending.

    Each dict:
        name          str        — instrument name
        ticker        str        — ticker symbol
        target_pct    float      — target weight %
        current_pct   float      — current weight %
        drift_pct     float      — current_pct - target_pct (positive = overweight)
        drift_abs     float      — abs(drift_pct)
        flagged       bool       — True if drift_abs >= threshold
        action        str        — "buy", "sell", or "hold"
        trade_pct     float      — size of trade needed as % of portfolio
        trade_amount  float|None — trade amount in portfolio currency (None if --value not given)
    """
    positions = portfolio.get("positions", [])
    results: list[dict] = []
    skipped_null: list[str] = []
    skipped_no_current: list[str] = []

    for pos in positions:
        instrument = pos.get("instrument", {})
        target_pct = pos.get("target_weight_pct")
        inst_name = instrument.get("name", "Unknown")
        inst_ticker = instrument.get("ticker", "")

        if target_pct is None:
            skipped_null.append(inst_name)
            continue

        # Determine current weight: prefer external map, fall back to portfolio.json field
        current_pct: float | None = None
        if current_weights_map is not None:
            current_pct = current_weights_map.get(inst_ticker) if inst_ticker else None
            if current_pct is None:
                current_pct = current_weights_map.get(inst_name)
        else:
            current_pct = pos.get("current_weight_pct")

        if current_pct is None:
            skipped_no_current.append(inst_name)
            continue

        drift_pct = round(current_pct - target_pct, 4)
        drift_abs = round(abs(drift_pct), 4)
        flagged = drift_abs >= threshold

        if drift_pct < 0:
            action = "buy"
        elif drift_pct > 0:
            action = "sell"
        else:
            action = "hold"

        trade_amount: float | None = None
        if portfolio_value is not None:
            trade_amount = round(portfolio_value * drift_abs / 100.0, 2)

        results.append(
            {
                "name": inst_name,
                "ticker": inst_ticker,
                "target_pct": round(target_pct, 4),
                "current_pct": round(current_pct, 4),
                "drift_pct": drift_pct,
                "drift_abs": drift_abs,
                "flagged": flagged,
                "action": action,
                "trade_pct": drift_abs,
                "trade_amount": trade_amount,
            }
        )

    if skipped_null:
        names = ", ".join(skipped_null)
        print(
            f"Warning: {len(skipped_null)} position(s) have no target_weight_pct and were skipped: {names}",
            file=sys.stderr,
        )
    if skipped_no_current:
        names = ", ".join(skipped_no_current)
        print(
            f"Warning: {len(skipped_no_current)} position(s) have no current weight and were skipped: {names}",
            file=sys.stderr,
        )

    results.sort(key=lambda x: x["drift_abs"], reverse=True)
    return results


def print_table(results: list[dict], threshold: float, portfolio_value: float | None) -> None:
    has_amounts = portfolio_value is not None
    header = f"{'#':<4} {'Ticker':<8} {'Name':<35} {'Target':>8} {'Current':>9} {'Drift':>8}   {'Action':<6}"
    if has_amounts:
        header += f"  {'Trade (€)':>12}"
    print(header)
    print("-" * (80 + (14 if has_amounts else 0)))
    for i, r in enumerate(results, 1):
        ticker_col = r["ticker"] if r["ticker"] else "—"
        flag = " ⚠" if r["flagged"] else "  "
        drift_str = f"{r['drift_pct']:+.2f}%"
        row = (
            f"{i:<4} {ticker_col:<8} {r['name']:<35} "
            f"{r['target_pct']:>7.2f}% {r['current_pct']:>8.2f}% "
            f"{drift_str:>8}{flag}  {r['action']:<6}"
        )
        if has_amounts and r["trade_amount"] is not None:
            row += f"  {r['trade_amount']:>12,.2f}"
        print(row)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute portfolio drift from targets and calculate rebalancing trades."
    )
    parser.add_argument(
        "portfolio",
        nargs="?",
        default="portfolio.json",
        help="Path to portfolio.json (default: portfolio.json)",
    )
    parser.add_argument(
        "--current",
        metavar="FILE",
        help=(
            "JSON file with current weights. "
            "Array: [{ticker, current_weight_pct}] or object: {ticker: weight_pct}. "
            "If omitted, reads current_weight_pct from portfolio.json positions."
        ),
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=5.0,
        metavar="PCT",
        help="Drift threshold in percentage points to flag positions (default: 5.0)",
    )
    parser.add_argument(
        "--value",
        type=float,
        default=None,
        metavar="AMOUNT",
        help="Current portfolio value in portfolio currency (enables trade amount sizing)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON object (for skill consumption)",
    )
    args = parser.parse_args()

    portfolio = load_portfolio(args.portfolio)

    current_weights_map: dict[str, float] | None = None
    if args.current:
        current_weights_map = load_current_weights(args.current)

    results = compute_drift(portfolio, current_weights_map, args.threshold, args.value)

    if args.json:
        flagged = [r for r in results if r["flagged"]]
        output = {
            "threshold_pct": args.threshold,
            "portfolio_value": args.value,
            "positions": results,
            "flagged_count": len(flagged),
            "flagged_positions": [r["ticker"] or r["name"] for r in flagged],
        }
        print(json.dumps(output, indent=2))
        return

    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")
    print(f"\nPortfolio Drift Analysis")
    print(f"Source: {args.portfolio}  |  version {version}  |  updated {updated}")
    print(f"Drift threshold: ±{args.threshold}%")
    if args.value:
        print(f"Portfolio value: {args.value:,.2f}")
    print()

    if not results:
        print("No positions with current and target weights found.")
        print("Supply current weights via --current FILE or add current_weight_pct to portfolio.json positions.")
        return

    print_table(results, threshold=args.threshold, portfolio_value=args.value)

    flagged = [r for r in results if r["flagged"]]
    if flagged:
        print(f"⚠  {len(flagged)} position(s) have drifted beyond ±{args.threshold}%:")
        for r in flagged:
            label = r["ticker"] or r["name"]
            direction = "overweight" if r["drift_pct"] > 0 else "underweight"
            trade_str = ""
            if r["trade_amount"] is not None:
                trade_str = f" — {r['action'].upper()} {r['trade_amount']:,.2f}"
            print(f"   • {label}: {r['drift_pct']:+.2f}% ({direction}){trade_str}")
    else:
        print(f"✓  All positions are within ±{args.threshold}% of their targets. No rebalancing needed.")
    print()


if __name__ == "__main__":
    main()
