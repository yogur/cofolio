#!/usr/bin/env python3
"""
concentration.py — Geographic and sector concentration analysis.

Reads portfolio.json, computes blended portfolio-level geographic and sector
breakdowns by weighting each instrument's splits by its target portfolio weight.

Usage:
    python concentration.py [portfolio.json] [--top N] [--json]

Arguments:
    portfolio.json   Path to portfolio JSON file (default: portfolio.json)
    --top N          Show top N entries per breakdown (default: all)
    --json           Output as JSON object (for skill consumption)
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


def compute_concentration(portfolio: dict) -> tuple[dict[str, float], dict[str, float], float]:
    """
    Returns (geographic_split, sector_split, covered_weight_pct).

    geographic_split and sector_split map region/sector name → portfolio-level
    weight (%). covered_weight_pct is the sum of target_weight_pct for positions
    that contributed data (used to detect incomplete portfolios).

    Positions with target_weight_pct=None are skipped with a warning.
    Positions missing geographic_split or sector_split emit a per-field warning
    and are excluded from that breakdown only.
    """
    positions = portfolio.get("positions", [])
    skipped_no_weight: list[str] = []
    geo: dict[str, float] = defaultdict(float)
    sector: dict[str, float] = defaultdict(float)
    covered_weight = 0.0

    for pos in positions:
        instrument = pos.get("instrument", {})
        pos_weight = pos.get("target_weight_pct")
        inst_name = instrument.get("name", "Unknown")

        if pos_weight is None:
            skipped_no_weight.append(inst_name)
            continue

        covered_weight += pos_weight
        scale = pos_weight / 100.0

        geo_split = instrument.get("geographic_split")
        if not geo_split:
            print(
                f"Warning: '{inst_name}' has no geographic_split — excluded from geographic breakdown.",
                file=sys.stderr,
            )
        else:
            for region, pct in geo_split.items():
                geo[region] += pct * scale

        sector_split = instrument.get("sector_split")
        if not sector_split:
            print(
                f"Warning: '{inst_name}' has no sector_split — excluded from sector breakdown.",
                file=sys.stderr,
            )
        else:
            for sec, pct in sector_split.items():
                sector[sec] += pct * scale

    if skipped_no_weight:
        names = ", ".join(skipped_no_weight)
        print(
            f"Warning: {len(skipped_no_weight)} position(s) have no target_weight_pct and were skipped: {names}",
            file=sys.stderr,
        )

    geo_rounded = {k: round(v, 2) for k, v in geo.items()}
    sector_rounded = {k: round(v, 2) for k, v in sector.items()}
    return geo_rounded, sector_rounded, round(covered_weight, 2)


def sort_and_trim(breakdown: dict[str, float], top_n: int | None) -> list[tuple[str, float]]:
    """Return items sorted descending by value, optionally capped at top_n."""
    items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    if top_n is not None:
        items = items[:top_n]
    return items


def print_breakdown(title: str, items: list[tuple[str, float]], total: float) -> None:
    print(f"\n{title}")
    print("-" * 45)
    for name, pct in items:
        bar = "#" * int(pct / 2)
        print(f"  {name:<30} {pct:>6.1f}%  {bar}")
    print("-" * 45)
    print(f"  {'Total shown':<30} {total:>6.1f}%")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute blended geographic and sector concentration from portfolio.json"
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
        default=None,
        metavar="N",
        help="Show top N entries per breakdown (default: all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON object {geographic_split: {...}, sector_split: {...}}",
    )
    args = parser.parse_args()

    portfolio = load_portfolio(args.portfolio)
    geo, sector, covered = compute_concentration(portfolio)

    if args.json:
        print(json.dumps({"geographic_split": geo, "sector_split": sector}, indent=2))
        return

    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")
    print(f"\nPortfolio Concentration Analysis")
    print(f"Source: {args.portfolio}  |  version {version}  |  updated {updated}")
    print(f"Portfolio weight covered: {covered:.1f}%")

    if not geo and not sector:
        print(
            "\nNo concentration data found. "
            "Check that positions have target_weight_pct, geographic_split, and sector_split set."
        )
        return

    if geo:
        geo_items = sort_and_trim(geo, args.top)
        geo_total = sum(v for _, v in geo_items)
        print_breakdown("Geographic Breakdown", geo_items, geo_total)

    if sector:
        sector_items = sort_and_trim(sector, args.top)
        sector_total = sum(v for _, v in sector_items)
        print_breakdown("Sector Breakdown", sector_items, sector_total)

    print()


if __name__ == "__main__":
    main()
