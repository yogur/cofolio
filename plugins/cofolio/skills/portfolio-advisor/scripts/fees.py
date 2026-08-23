#!/usr/bin/env python3
"""
fees.py — Fee drag analysis.

Reads portfolio.json, computes the weighted average TER across all positions,
and projects cumulative fee drag over configurable time horizons at an assumed
annual growth rate with optional monthly contributions.

Growth rate and contribution amount originate from investor-profile.md and are
passed as CLI arguments by the invoking skill.

Usage:
    python fees.py [portfolio.json] [--growth RATE] [--contribution AMOUNT]
                   [--initial AMOUNT] [--horizons YEARS] [--json]

Arguments:
    portfolio.json      Path to portfolio JSON file (default: portfolio.json)
    --growth RATE       Assumed annual growth rate in % (default: 7.0)
    --contribution AMT  Monthly contribution in portfolio currency (default: 0)
    --initial AMT       Current portfolio value in portfolio currency (default: 0)
    --horizons YEARS    Comma-separated projection horizons in years (default: 10,20,30)
    --json              Output as JSON object (for skill consumption)
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


def compute_weighted_ter(portfolio: dict) -> tuple[float, list[dict]]:
    """
    Returns (weighted_avg_ter_pct, breakdown) where breakdown is a list of
    per-position dicts with name, weight_pct, ter_pct, and contribution_to_ter.

    Positions with target_weight_pct=None are skipped (with a warning).
    Positions without ter_pct (e.g. stocks) contribute 0 to the weighted TER.
    """
    positions = portfolio.get("positions", [])
    skipped: list[str] = []
    breakdown: list[dict] = []
    weighted_ter = 0.0

    for pos in positions:
        instrument = pos.get("instrument", {})
        pos_weight = pos.get("target_weight_pct")
        inst_name = instrument.get("name", "Unknown")

        if pos_weight is None:
            skipped.append(inst_name)
            continue

        ter = instrument.get("ter_pct")
        if ter is None:
            ter = 0.0  # stocks and other non-fund instruments have no TER

        contribution = pos_weight * ter / 100.0
        weighted_ter += contribution

        breakdown.append(
            {
                "name": inst_name,
                "type": instrument.get("type", "unknown"),
                "weight_pct": pos_weight,
                "ter_pct": ter,
                "contribution_to_ter": round(contribution, 6),
            }
        )

    if skipped:
        names = ", ".join(skipped)
        print(
            f"Warning: {len(skipped)} position(s) have no target_weight_pct and were skipped: {names}",
            file=sys.stderr,
        )

    return round(weighted_ter, 6), breakdown


def future_value(
    initial: float,
    monthly_contribution: float,
    annual_rate: float,
    years: int,
) -> float:
    """
    Computes future value with monthly compounding.

    FV = P0 * (1 + r_m)^(n*12) + C * ((1 + r_m)^(n*12) - 1) / r_m

    where r_m = (1 + annual_rate)^(1/12) - 1

    Handles the edge case of annual_rate == 0 (no division by zero).
    """
    months = years * 12
    if annual_rate == 0.0:
        return initial + monthly_contribution * months

    r_monthly = (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0
    growth_factor = (1.0 + r_monthly) ** months
    fv_lump = initial * growth_factor
    fv_contributions = monthly_contribution * (growth_factor - 1.0) / r_monthly
    return fv_lump + fv_contributions


def project_fee_drag(
    weighted_ter_pct: float,
    growth_rate_pct: float,
    monthly_contribution: float,
    initial_value: float,
    horizons: list[int],
) -> list[dict]:
    """
    For each horizon, returns a dict with:
        years           int    — projection horizon
        fv_gross        float  — future value at gross growth rate
        fv_net          float  — future value at net growth rate (gross - TER)
        fee_drag        float  — cumulative fee cost (fv_gross - fv_net)
        fee_drag_pct    float  — fee drag as % of gross FV
    """
    g = growth_rate_pct / 100.0
    ter = weighted_ter_pct / 100.0
    net_rate = g - ter

    results = []
    for n in horizons:
        fv_gross = future_value(initial_value, monthly_contribution, g, n)
        fv_net = future_value(initial_value, monthly_contribution, net_rate, n)
        drag = fv_gross - fv_net
        drag_pct = (drag / fv_gross * 100.0) if fv_gross > 0 else 0.0

        results.append(
            {
                "years": n,
                "fv_gross": round(fv_gross, 2),
                "fv_net": round(fv_net, 2),
                "fee_drag": round(drag, 2),
                "fee_drag_pct": round(drag_pct, 2),
            }
        )
    return results


def print_results(
    portfolio_path: str,
    portfolio: dict,
    weighted_ter: float,
    breakdown: list[dict],
    projections: list[dict],
    growth_rate_pct: float,
    monthly_contribution: float,
    initial_value: float,
) -> None:
    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")

    print(f"\nPortfolio Fee Drag Analysis")
    print(f"Source: {portfolio_path}  |  version {version}  |  updated {updated}")
    print(
        f"Assumptions: {growth_rate_pct}% annual growth  |  "
        f"{monthly_contribution:,.0f}/mo contribution  |  "
        f"{initial_value:,.0f} initial value"
    )

    # Per-position TER breakdown
    print(f"\n{'Position':<40} {'Weight':>8}   {'TER':>6}   {'Contrib':>8}")
    print("-" * 68)
    for b in sorted(breakdown, key=lambda x: x["contribution_to_ter"], reverse=True):
        ter_str = f"{b['ter_pct']:.3f}%" if b["ter_pct"] else "—"
        print(
            f"{b['name']:<40} {b['weight_pct']:>7.1f}%   "
            f"{ter_str:>6}   {b['contribution_to_ter']:>7.4f}%"
        )
    print("-" * 68)
    print(f"{'Weighted Average TER':<40} {'':>8}   {'':>6}   {weighted_ter:>7.4f}%")

    # Fee drag projections
    print(f"\nFee Drag Projections (weighted TER = {weighted_ter:.4f}%)")
    print(
        f"\n{'Horizon':<10} {'Gross FV':>14} {'Net FV':>14} {'Fee Drag':>14} {'Drag %':>8}"
    )
    print("-" * 64)
    for p in projections:
        print(
            f"{p['years']:<4} years  "
            f"{p['fv_gross']:>14,.0f}  "
            f"{p['fv_net']:>14,.0f}  "
            f"{p['fee_drag']:>14,.0f}  "
            f"{p['fee_drag_pct']:>7.1f}%"
        )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute weighted average TER and project fee drag from portfolio.json"
    )
    parser.add_argument(
        "portfolio",
        nargs="?",
        default="portfolio.json",
        help="Path to portfolio.json (default: portfolio.json)",
    )
    parser.add_argument(
        "--growth",
        type=float,
        default=7.0,
        metavar="RATE",
        help="Assumed annual growth rate in %% (default: 7.0)",
    )
    parser.add_argument(
        "--contribution",
        type=float,
        default=0.0,
        metavar="AMOUNT",
        help="Monthly contribution in portfolio currency (default: 0)",
    )
    parser.add_argument(
        "--initial",
        type=float,
        default=0.0,
        metavar="AMOUNT",
        help="Current portfolio value in portfolio currency (default: 0)",
    )
    parser.add_argument(
        "--horizons",
        default="10,20,30",
        metavar="YEARS",
        help="Comma-separated projection horizons in years (default: 10,20,30)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON object {weighted_avg_ter_pct, fee_drag_10y, ...}",
    )
    args = parser.parse_args()

    try:
        horizons = [int(h.strip()) for h in args.horizons.split(",") if h.strip()]
    except ValueError:
        print("Error: --horizons must be a comma-separated list of integers.", file=sys.stderr)
        sys.exit(1)

    if not horizons:
        print("Error: --horizons cannot be empty.", file=sys.stderr)
        sys.exit(1)

    portfolio = load_portfolio(args.portfolio)
    weighted_ter, breakdown = compute_weighted_ter(portfolio)
    projections = project_fee_drag(
        weighted_ter_pct=weighted_ter,
        growth_rate_pct=args.growth,
        monthly_contribution=args.contribution,
        initial_value=args.initial,
        horizons=horizons,
    )

    if args.json:
        output: dict = {"weighted_avg_ter_pct": weighted_ter}
        for p in projections:
            output[f"fee_drag_{p['years']}y"] = p["fee_drag"]
        print(json.dumps(output, indent=2))
        return

    print_results(
        portfolio_path=args.portfolio,
        portfolio=portfolio,
        weighted_ter=weighted_ter,
        breakdown=breakdown,
        projections=projections,
        growth_rate_pct=args.growth,
        monthly_contribution=args.contribution,
        initial_value=args.initial,
    )


if __name__ == "__main__":
    main()
