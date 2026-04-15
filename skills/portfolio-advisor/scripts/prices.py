#!/usr/bin/env python3
"""
prices.py — Portfolio price fetcher and current-weight calculator.

Reads portfolio.json, fetches latest prices for all tickers via yfinance,
and computes current portfolio values and weights from current_holdings
(share counts stored in each position).

Usage:
    python prices.py [portfolio.json] [--exchange-suffix SUFFIX] [--json]

Arguments:
    portfolio.json         Path to portfolio JSON file (default: portfolio.json)
    --exchange-suffix SUF  Default suffix for tickers without one (e.g., DE for XETRA)
    --json                 Output as JSON object (for skill consumption)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print(
        "Error: yfinance is not installed. Run: pip install yfinance",
        file=sys.stderr,
    )
    sys.exit(1)


# Known exchange-to-yfinance suffix mappings
EXCHANGE_SUFFIX_MAP: dict[str, str] = {
    "XETRA": "DE",
    "Euronext Amsterdam": "AS",
    "Euronext Paris": "PA",
    "LSE": "L",
    "London Stock Exchange": "L",
    "SIX": "SW",
    "Borsa Italiana": "MI",
    "BME": "MC",
    "TSE": "T",
    "ASX": "AX",
    "NYSE": "",
    "NASDAQ": "",
}


def load_portfolio(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    with p.open() as f:
        return json.load(f)


def resolve_ticker(ticker: str, exchange: str, suffix: str | None) -> list[str]:
    """
    Return a list of yfinance ticker candidates to try, in priority order.
    """
    candidates: list[str] = []

    # 1. Try ticker as-is
    candidates.append(ticker)

    # 2. If --exchange-suffix provided and ticker has no dot, try with suffix
    if suffix and "." not in ticker:
        candidates.append(f"{ticker}.{suffix}")

    # 3. Map from instrument.exchange field
    if exchange:
        mapped_suffix = EXCHANGE_SUFFIX_MAP.get(exchange)
        if mapped_suffix is not None and "." not in ticker:
            suffixed = f"{ticker}.{mapped_suffix}" if mapped_suffix else ticker
            if suffixed not in candidates:
                candidates.append(suffixed)

    return candidates


def fetch_price(candidates: list[str]) -> dict | None:
    """
    Try each ticker candidate until one returns valid price data.
    Returns a dict with price info or None if all fail.
    """
    for candidate in candidates:
        try:
            t = yf.Ticker(candidate)
            info = t.fast_info
            price = getattr(info, "last_price", None)
            if price is None or price <= 0:
                continue
            currency = getattr(info, "currency", None) or "Unknown"
            # Get the last trade date from history
            price_date = None
            try:
                hist = t.history(period="5d")
                if not hist.empty:
                    price_date = str(hist.index[-1].date())
            except Exception:
                pass
            return {
                "ticker_resolved": candidate,
                "price": round(float(price), 4),
                "currency": currency,
                "price_date": price_date,
            }
        except Exception:
            continue
    return None


def process_positions(
    portfolio: dict, exchange_suffix: str | None
) -> tuple[list[dict], list[str]]:
    """
    Fetch prices for all positions and compute values/weights if holdings exist.

    Returns (positions_data, failed_tickers).
    """
    positions = portfolio.get("positions", [])
    results: list[dict] = []
    failed: list[str] = []
    has_any_holdings = False

    for pos in positions:
        instrument = pos.get("instrument", {})
        ticker = instrument.get("ticker", "")
        inst_name = instrument.get("name", "Unknown")
        exchange = instrument.get("exchange", "")
        holdings = pos.get("current_holdings")

        if not ticker:
            print(
                f"Warning: position '{inst_name}' has no ticker, skipping price fetch.",
                file=sys.stderr,
            )
            continue

        candidates = resolve_ticker(ticker, exchange, exchange_suffix)
        price_data = fetch_price(candidates)

        if price_data is None:
            failed.append(ticker)
            print(
                f"Warning: could not fetch price for '{ticker}' "
                f"(tried: {', '.join(candidates)}).",
                file=sys.stderr,
            )
            continue

        entry: dict = {
            "name": inst_name,
            "ticker": ticker,
            "ticker_resolved": price_data["ticker_resolved"],
            "price": price_data["price"],
            "currency": price_data["currency"],
            "price_date": price_data["price_date"],
            "shares": None,
            "value": None,
            "current_weight_pct": None,
        }

        if holdings is not None:
            has_any_holdings = True
            shares = float(holdings)
            value = round(shares * price_data["price"], 2)
            entry["shares"] = shares
            entry["value"] = value

        results.append(entry)

    # Compute weights if any position has holdings
    if has_any_holdings:
        total_value = sum(r["value"] for r in results if r["value"] is not None)
        if total_value > 0:
            for r in results:
                if r["value"] is not None:
                    r["current_weight_pct"] = round(r["value"] / total_value * 100, 2)

    # Check for mixed currencies
    currencies = {r["currency"] for r in results}
    if len(currencies) > 1:
        print(
            f"Warning: mixed currencies detected ({', '.join(sorted(currencies))}). "
            "Weights assume values are comparable.",
            file=sys.stderr,
        )

    return results, failed


def build_output(results: list[dict], failed: list[str]) -> dict:
    """Build the JSON output structure."""
    has_holdings = any(r["value"] is not None for r in results)
    total_value: float | None = None
    current_weights: dict[str, float] | None = None

    if has_holdings:
        total_value = round(
            sum(r["value"] for r in results if r["value"] is not None), 2
        )
        current_weights = {
            r["ticker"]: r["current_weight_pct"]
            for r in results
            if r["current_weight_pct"] is not None
        }

    return {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "positions": results,
        "failed_tickers": failed,
        "total_value": total_value,
        "current_weights": current_weights,
    }


def print_table(results: list[dict], failed: list[str], portfolio_path: str) -> None:
    has_holdings = any(r["value"] is not None for r in results)

    if has_holdings:
        header = (
            f"{'#':<4} {'Ticker':<8} {'Name':<35} "
            f"{'Price':>10} {'Shares':>8} {'Value':>12} {'Weight':>8}"
        )
        print(header)
        print("-" * 90)
        for i, r in enumerate(results, 1):
            ticker_col = r["ticker"] if r["ticker"] else "—"
            if r["value"] is not None:
                print(
                    f"{i:<4} {ticker_col:<8} {r['name']:<35} "
                    f"{r['price']:>10,.2f} {r['shares']:>8.2f} "
                    f"{r['value']:>12,.2f} {r['current_weight_pct']:>7.2f}%"
                )
            else:
                print(
                    f"{i:<4} {ticker_col:<8} {r['name']:<35} "
                    f"{r['price']:>10,.2f} {'—':>8} {'—':>12} {'—':>8}"
                )
        total_value = sum(r["value"] for r in results if r["value"] is not None)
        print()
        print(f"  Total portfolio value: {total_value:>12,.2f}")
    else:
        header = f"{'#':<4} {'Ticker':<8} {'Resolved':<12} {'Name':<35} {'Price':>10} {'Currency':<6}"
        print(header)
        print("-" * 80)
        for i, r in enumerate(results, 1):
            ticker_col = r["ticker"] if r["ticker"] else "—"
            resolved = (
                r["ticker_resolved"] if r["ticker_resolved"] != r["ticker"] else ""
            )
            print(
                f"{i:<4} {ticker_col:<8} {resolved:<12} {r['name']:<35} "
                f"{r['price']:>10,.2f} {r['currency']:<6}"
            )

    if failed:
        print()
        tickers = ", ".join(failed)
        print(f"  {len(failed)} ticker(s) could not be resolved: {tickers}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch latest prices for portfolio positions and compute current weights."
    )
    parser.add_argument(
        "portfolio",
        nargs="?",
        default="portfolio.json",
        help="Path to portfolio.json (default: portfolio.json)",
    )
    parser.add_argument(
        "--exchange-suffix",
        metavar="SUFFIX",
        default=None,
        help=(
            "Default suffix to append to tickers without one "
            "(e.g., DE for XETRA). Only applied to tickers without a dot."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON object (for skill consumption)",
    )
    args = parser.parse_args()

    portfolio = load_portfolio(args.portfolio)
    results, failed = process_positions(portfolio, args.exchange_suffix)

    if args.json:
        output = build_output(results, failed)
        print(json.dumps(output, indent=2))
        return

    version = portfolio.get("version", "?")
    updated = portfolio.get("updated", "unknown")
    print("\nPortfolio Price Snapshot")
    print(f"Source: {args.portfolio}  |  version {version}  |  updated {updated}")
    print(f"As of: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
    print()

    if not results:
        if failed:
            print(f"No prices could be fetched. Failed tickers: {', '.join(failed)}")
        else:
            print("No positions with tickers found in portfolio.")
        return

    print_table(results, failed, args.portfolio)


if __name__ == "__main__":
    main()
