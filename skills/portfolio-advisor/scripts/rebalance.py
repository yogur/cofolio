#!/usr/bin/env python3
"""
rebalance.py — Contribution-based rebalancing optimizer.

Given monthly contribution amount, current weights, and target weights,
calculates how to allocate contributions to minimize drift without selling.
Selling is suggested only when contributions alone cannot correct drift
within a configurable timeframe.

Usage:
    python rebalance.py [portfolio.json] [--current FILE] [--contribution AMOUNT]
                        [--value AMOUNT] [--threshold PCT] [--timeframe MONTHS] [--json]

Arguments:
    portfolio.json       Path to portfolio JSON file (default: portfolio.json)
    --current FILE       JSON file with current weights.
                         Array: [{ticker, current_weight_pct}] or object: {ticker: weight_pct}
                         If omitted, reads current_weight_pct from portfolio.json positions.
    --contribution AMT   Monthly contribution amount in portfolio currency (required)
    --value AMOUNT       Current portfolio value in portfolio currency (required)
    --threshold PCT      Drift threshold to flag sell suggestions in % points (default: 5.0)
    --timeframe MONTHS   Months beyond which selling is suggested (default: 12)
    --json               Output as JSON object (for skill consumption)
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


def optimize_contributions(
    portfolio: dict,
    current_weights_map: dict[str, float] | None,
    contribution: float,
    portfolio_value: float,
    threshold: float,
    timeframe_months: int,
) -> dict:
    """
    Compute the optimal contribution allocation to minimize drift without selling.

    Algorithm:
      1. New portfolio total = current value + contribution.
      2. For each underweight position, compute the buy needed to hit its new target
         value (= target_pct * new_total).
      3. If total buys needed <= contribution: buy exactly, hold remainder as cash.
      4. If total buys needed > contribution: scale each buy proportionally to
         the position's underweight magnitude.
      5. Estimate months to full rebalance = remaining underweight / monthly contribution.
      6. If months_to_target > timeframe and position is still >threshold% overweight,
         suggest selling the excess.

    Returns a dict with keys:
        contribution, portfolio_value, new_total, positions,
        unallocated, fully_rebalanced, months_to_target, sell_suggestions
    """
    positions = portfolio.get("positions", [])
    new_total = portfolio_value + contribution

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

        current_value = current_pct / 100.0 * portfolio_value
        new_target_value = target_pct / 100.0 * new_total
        drift_pct = round(current_pct - target_pct, 4)
        # Only underweight positions receive contributions
        buy_needed = max(0.0, new_target_value - current_value)

        results.append(
            {
                "name": inst_name,
                "ticker": inst_ticker,
                "target_pct": round(target_pct, 4),
                "current_pct": round(current_pct, 4),
                "drift_pct": drift_pct,
                "current_value": round(current_value, 2),
                "new_target_value": round(new_target_value, 2),
                "buy_needed": round(buy_needed, 2),
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

    # ── Allocate contribution ──────────────────────────────────────────────────
    total_buy_needed = sum(r["buy_needed"] for r in results)

    if total_buy_needed <= contribution:
        # Full rebalance achievable this month
        for r in results:
            r["allocation"] = r["buy_needed"]
        unallocated = round(contribution - total_buy_needed, 2)
        fully_rebalanced = True
    else:
        # Scale down proportionally by each position's buy_needed share
        scale = contribution / total_buy_needed if total_buy_needed > 0 else 0.0
        for r in results:
            r["allocation"] = round(r["buy_needed"] * scale, 2)
        unallocated = 0.0
        fully_rebalanced = False

    # ── Post-contribution weights ──────────────────────────────────────────────
    for r in results:
        post_value = r["current_value"] + r["allocation"]
        r["post_pct"] = round(post_value / new_total * 100, 4)
        r["post_drift_pct"] = round(r["post_pct"] - r["target_pct"], 4)
        r["allocation_pct"] = round(r["allocation"] / contribution * 100, 2) if contribution > 0 else 0.0

    # ── Months-to-target estimate ──────────────────────────────────────────────
    months_to_target: float | None = None
    if not fully_rebalanced and contribution > 0:
        remaining_underweight = sum(
            max(0.0, r["new_target_value"] - (r["current_value"] + r["allocation"]))
            for r in results
        )
        months_to_target = round(remaining_underweight / contribution, 1)

    # ── Sell suggestions ───────────────────────────────────────────────────────
    sell_suggestions: list[dict] = []
    if months_to_target is not None and months_to_target > timeframe_months:
        for r in results:
            if r["post_drift_pct"] > threshold:
                post_value = r["current_value"] + r["allocation"]
                sell_amount = round(post_value - r["new_target_value"], 2)
                if sell_amount > 0:
                    sell_suggestions.append(
                        {
                            "ticker": r["ticker"],
                            "name": r["name"],
                            "post_drift_pct": r["post_drift_pct"],
                            "sell_amount": sell_amount,
                        }
                    )

    return {
        "contribution": contribution,
        "portfolio_value": portfolio_value,
        "new_total": round(new_total, 2),
        "positions": results,
        "unallocated": unallocated,
        "fully_rebalanced": fully_rebalanced,
        "months_to_target": months_to_target,
        "sell_suggestions": sell_suggestions,
    }


def print_table(result: dict) -> None:
    positions = result["positions"]
    contribution = result["contribution"]

    header = (
        f"{'#':<4} {'Ticker':<8} {'Name':<35} {'Target':>8} {'Current':>9} "
        f"{'Drift':>8}   {'Alloc (€)':>10}  {'Alloc %':>7}  {'Post':>8}"
    )
    print(header)
    print("-" * 105)

    for i, r in enumerate(positions, 1):
        ticker_col = r["ticker"] if r["ticker"] else "—"
        drift_str = f"{r['drift_pct']:+.2f}%"
        flag = " ⚠" if abs(r["drift_pct"]) >= 5.0 else "  "
        post_str = f"{r['post_pct']:.2f}%"

        row = (
            f"{i:<4} {ticker_col:<8} {r['name']:<35} "
            f"{r['target_pct']:>7.2f}% {r['current_pct']:>8.2f}% "
            f"{drift_str:>8}{flag}  {r['allocation']:>10,.2f}  "
            f"{r['allocation_pct']:>6.1f}%  {post_str:>8}"
        )
        print(row)

    print()
    print(f"  Total contribution:  {contribution:>12,.2f}")
    print(f"  Allocated:           {contribution - result['unallocated']:>12,.2f}")
    if result["unallocated"] > 0:
        print(f"  Unallocated (cash):  {result['unallocated']:>12,.2f}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Optimize monthly contributions to minimize portfolio drift without selling."
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
        "--contribution",
        type=float,
        required=True,
        metavar="AMOUNT",
        help="Monthly contribution amount in portfolio currency",
    )
    parser.add_argument(
        "--value",
        type=float,
        required=True,
        metavar="AMOUNT",
        help="Current portfolio value in portfolio currency",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=5.0,
        metavar="PCT",
        help="Drift threshold in percentage points for sell suggestions (default: 5.0)",
    )
    parser.add_argument(
        "--timeframe",
        type=int,
        default=12,
        metavar="MONTHS",
        help="Months beyond which selling is suggested instead of waiting (default: 12)",
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

    result = optimize_contributions(
        portfolio,
        current_weights_map,
        args.contribution,
        args.value,
        args.threshold,
        args.timeframe,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")
    print(f"\nRebalancing Optimizer — Contribution Allocation")
    print(f"Source: {args.portfolio}  |  version {version}  |  updated {updated}")
    print(f"Portfolio value: {args.value:,.2f}  |  Monthly contribution: {args.contribution:,.2f}")
    print(f"Sell-suggestion threshold: >{args.threshold}% drift  |  Timeframe: {args.timeframe} months")
    print()

    if not result["positions"]:
        print("No positions with current and target weights found.")
        print(
            "Supply current weights via --current FILE or add current_weight_pct to portfolio.json positions."
        )
        return

    print_table(result)

    if result["fully_rebalanced"]:
        print("✓  Full rebalance achieved with this month's contribution.")
        if result["unallocated"] > 0:
            print(
                f"   {result['unallocated']:,.2f} unallocated — consider holding as cash "
                "or adding to the most underweight position next month."
            )
    else:
        mtt = result["months_to_target"]
        print("→  Partial rebalance: contributions allocated proportionally to underweight positions.")
        if mtt is not None:
            print(f"   Estimated {mtt:.1f} months to fully rebalance via contributions alone.")

    sell = result["sell_suggestions"]
    if sell:
        print()
        print(
            f"⚠  Drift cannot be corrected within {args.timeframe} months via contributions alone."
        )
        print("   Consider selling the following overweight positions:")
        for s in sell:
            label = s["ticker"] or s["name"]
            print(f"   • {label}: +{s['post_drift_pct']:.2f}% overweight — SELL {s['sell_amount']:,.2f}")

    print()


if __name__ == "__main__":
    main()
