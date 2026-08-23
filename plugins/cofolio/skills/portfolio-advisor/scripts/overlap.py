#!/usr/bin/env python3
"""
overlap.py — Look-through single-stock exposure analysis.

Reads portfolio.json, computes blended portfolio-level exposure for each
underlying stock by weighting ETF top-holdings by position target weights.
Individual stock positions are counted directly at their target weight.

Usage:
    python overlap.py [portfolio.json] [--top N] [--threshold PCT] [--json]

Arguments:
    portfolio.json   Path to portfolio JSON file (default: portfolio.json)
    --top N          Show top N stocks by exposure (default: 10)
    --threshold PCT  Flag stocks exceeding this % of portfolio (default: 3.0)
    --json           Output as JSON array (for skill consumption)
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_portfolio(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    with p.open() as f:
        return json.load(f)


def compute_overlap(portfolio: dict, top_n: int, threshold: float) -> list[dict]:
    """
    Returns a list of dicts sorted by total_pct descending, capped at top_n.

    Each dict:
        ticker      str   — ticker symbol (empty string if unavailable)
        name        str   — human-readable name
        total_pct   float — blended portfolio-level exposure (%)
        flagged     bool  — True if total_pct >= threshold
        sources     list  — breakdown by contributing position
    """
    positions = portfolio.get("positions", [])

    # key → {name, ticker, total_pct, sources}
    exposure: dict[str, dict] = defaultdict(
        lambda: {"name": "", "ticker": "", "total_pct": 0.0, "sources": []}
    )
    skipped: list[str] = []

    for pos in positions:
        instrument = pos.get("instrument", {})
        pos_weight = pos.get("target_weight_pct")
        inst_name = instrument.get("name", "Unknown")
        inst_type = instrument.get("type", "").lower()
        inst_ticker = instrument.get("ticker", "")

        if pos_weight is None:
            skipped.append(inst_name)
            continue

        if inst_type == "etf":
            top_holdings = instrument.get("top_holdings") or []
            if not top_holdings:
                print(
                    f"Warning: ETF '{inst_name}' has no top_holdings — excluded from overlap.",
                    file=sys.stderr,
                )
                continue

            for holding in top_holdings:
                h_ticker = holding.get("ticker", "")
                h_name = holding.get("name", h_ticker)
                h_weight = holding.get("weight_pct", 0.0)

                # Blended exposure = position_weight% × holding_weight% / 100
                contribution = pos_weight * h_weight / 100.0
                key = h_ticker if h_ticker else h_name

                exposure[key]["name"] = h_name
                exposure[key]["ticker"] = h_ticker
                exposure[key]["total_pct"] += contribution
                exposure[key]["sources"].append(
                    {
                        "position": inst_name,
                        "position_weight_pct": pos_weight,
                        "holding_weight_pct": h_weight,
                        "contribution_pct": round(contribution, 4),
                    }
                )

        elif inst_type == "stock":
            key = inst_ticker if inst_ticker else inst_name
            exposure[key]["name"] = inst_name
            exposure[key]["ticker"] = inst_ticker
            exposure[key]["total_pct"] += pos_weight
            exposure[key]["sources"].append(
                {
                    "position": inst_name,
                    "position_weight_pct": pos_weight,
                    "holding_weight_pct": 100.0,
                    "contribution_pct": round(pos_weight, 4),
                }
            )

        # bonds, cash, and other types are not decomposed into single-stock exposures

    if skipped:
        names = ", ".join(skipped)
        print(
            f"Warning: {len(skipped)} position(s) have no target_weight_pct and were skipped: {names}",
            file=sys.stderr,
        )

    results = sorted(exposure.values(), key=lambda x: x["total_pct"], reverse=True)

    for r in results:
        r["total_pct"] = round(r["total_pct"], 4)
        r["flagged"] = r["total_pct"] >= threshold

    return results[:top_n]


def print_table(results: list[dict], threshold: float) -> None:
    print(f"\n{'#':<4} {'Ticker':<8} {'Name':<35} {'Exposure':>10}   Notes")
    print("-" * 70)
    for i, r in enumerate(results, 1):
        ticker_col = r["ticker"] if r["ticker"] else "—"
        flag = f"  ⚠  exceeds {threshold}%" if r["flagged"] else ""
        print(f"{i:<4} {ticker_col:<8} {r['name']:<35} {r['total_pct']:>9.2f}%{flag}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute look-through single-stock exposure from portfolio.json"
    )
    parser.add_argument(
        "portfolio",
        nargs="?",
        default="portfolio.json",
        help="Path to portfolio.json (default: portfolio.json)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Show top N stock exposures (default: 10)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        metavar="PCT",
        help="Flag stocks exceeding this %% of total portfolio (default: 3.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON array [{ticker, name, total_pct}, ...]",
    )
    args = parser.parse_args()

    portfolio = load_portfolio(args.portfolio)
    results = compute_overlap(portfolio, top_n=args.top, threshold=args.threshold)

    if args.json:
        output = [
            {"ticker": r["ticker"], "name": r["name"], "total_pct": r["total_pct"]}
            for r in results
        ]
        print(json.dumps(output, indent=2))
        return

    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")
    print(f"\nPortfolio Overlap Analysis")
    print(f"Source: {args.portfolio}  |  version {version}  |  updated {updated}")
    print(f"Concentration threshold: {args.threshold}%  |  Showing top {args.top}")

    if not results:
        print("\nNo stock exposures found. Check that positions have target_weight_pct set.")
        return

    print_table(results, threshold=args.threshold)

    flagged = [r for r in results if r["flagged"]]
    if flagged:
        names = ", ".join(r["ticker"] or r["name"] for r in flagged)
        print(f"⚠  {len(flagged)} stock(s) exceed the {args.threshold}% threshold: {names}")
    else:
        print(f"✓  No single-stock look-through exposure exceeds {args.threshold}%.")
    print()


if __name__ == "__main__":
    main()
