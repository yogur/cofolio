#!/usr/bin/env python3
"""
dca.py — DCA (Dollar Cost Averaging) allocation calculator.

Given a monthly contribution amount and portfolio.json target weights,
computes the ideal allocation to each position. This is the simple,
no-drift-awareness split — for drift-correcting allocation, use rebalance.py.

Usage:
    python dca.py [portfolio.json] [--contribution AMOUNT] [--json]

Arguments:
    portfolio.json       Path to portfolio JSON file (default: portfolio.json)
    --contribution AMT   Monthly contribution amount in portfolio currency (required)
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


def compute_dca(portfolio: dict, contribution: float) -> dict:
    """
    Compute ideal DCA allocation based on target weights.

    Returns a dict with keys:
        contribution, positions, total_allocated, total_weight_pct
    """
    positions = portfolio.get("positions", [])
    results: list[dict] = []
    skipped_null: list[str] = []

    for pos in positions:
        instrument = pos.get("instrument", {})
        target_pct = pos.get("target_weight_pct")
        inst_name = instrument.get("name", "Unknown")
        inst_ticker = instrument.get("ticker", "")

        if target_pct is None:
            skipped_null.append(inst_name)
            continue

        allocation = round(contribution * target_pct / 100.0, 2)

        results.append(
            {
                "name": inst_name,
                "ticker": inst_ticker,
                "target_weight_pct": round(target_pct, 4),
                "allocation": allocation,
            }
        )

    if skipped_null:
        names = ", ".join(skipped_null)
        print(
            f"Warning: {len(skipped_null)} position(s) have no target_weight_pct and were skipped: {names}",
            file=sys.stderr,
        )

    total_weight = sum(r["target_weight_pct"] for r in results)
    total_allocated = sum(r["allocation"] for r in results)

    if abs(total_weight - 100.0) > 1.0:
        if total_weight < 100.0:
            print(
                f"Warning: target weights sum to {total_weight:.1f}% — "
                f"{contribution - total_allocated:.2f} of the contribution is unallocated.",
                file=sys.stderr,
            )
        else:
            print(
                f"Warning: target weights sum to {total_weight:.1f}% — "
                f"allocations exceed the contribution by {total_allocated - contribution:.2f}.",
                file=sys.stderr,
            )

    return {
        "contribution": contribution,
        "positions": results,
        "total_allocated": round(total_allocated, 2),
        "total_weight_pct": round(total_weight, 4),
    }


def print_table(result: dict) -> None:
    positions = result["positions"]

    header = f"{'#':<4} {'Ticker':<8} {'Name':<35} {'Target':>8}   {'Allocation':>12}"
    print(header)
    print("-" * 72)

    for i, r in enumerate(positions, 1):
        ticker_col = r["ticker"] if r["ticker"] else "—"
        print(
            f"{i:<4} {ticker_col:<8} {r['name']:<35} "
            f"{r['target_weight_pct']:>7.2f}%   {r['allocation']:>12,.2f}"
        )

    print("-" * 72)
    print(
        f"{'':4} {'':8} {'Total':<35} "
        f"{result['total_weight_pct']:>7.1f}%   {result['total_allocated']:>12,.2f}"
    )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute ideal DCA allocation based on portfolio target weights."
    )
    parser.add_argument(
        "portfolio",
        nargs="?",
        default="portfolio.json",
        help="Path to portfolio.json (default: portfolio.json)",
    )
    parser.add_argument(
        "--contribution",
        type=float,
        required=True,
        metavar="AMOUNT",
        help="Monthly contribution amount in portfolio currency",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON object (for skill consumption)",
    )
    args = parser.parse_args()

    if args.contribution <= 0:
        print("Error: --contribution must be a positive amount.", file=sys.stderr)
        sys.exit(1)

    portfolio = load_portfolio(args.portfolio)
    result = compute_dca(portfolio, args.contribution)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")
    print("\nDCA Allocation — Ideal Monthly Split")
    print(f"Source: {args.portfolio}  |  version {version}  |  updated {updated}")
    print(f"Monthly contribution: {args.contribution:,.2f}")
    print()

    if not result["positions"]:
        print("No positions with target weights found.")
        return

    print_table(result)

    print("This is the ideal split assuming no drift from targets.")
    print("For drift-aware allocation, use rebalance.py with current weights.")
    print()


if __name__ == "__main__":
    main()
