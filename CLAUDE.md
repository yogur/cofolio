# CoFolio — Developer Notes

## Scripts (`scripts/`)

- All analysis scripts read `portfolio.json` from a path passed as a positional CLI argument (default: `portfolio.json` in CWD).
- Scripts accept `--json` to emit machine-readable output for skill consumption. The JSON format matches the `analysis` section schema in `portfolio.json` (see PRD Section 4 / Stage 5).
- `overlap.py`: position `type` field drives logic — `"etf"` decomposes `top_holdings`, `"stock"` counts directly at `target_weight_pct`. Other types (bonds, cash) are silently skipped.
- `fees.py`: computes weighted average TER and projects fee drag using monthly compounding. Accepts `--growth` (annual %), `--contribution` (monthly amount), `--initial` (starting value), `--horizons` (comma-separated years). Stocks/positions without `ter_pct` contribute 0 to the weighted TER. `--json` emits `{weighted_avg_ter_pct, fee_drag_10y, fee_drag_20y, fee_drag_30y}` (keys follow `fee_drag_<N>y` pattern for any horizons).
- `concentration.py`: computes blended geographic and sector breakdowns by weighting each instrument's `geographic_split` / `sector_split` by `target_weight_pct / 100`. Both ETFs and stocks contribute if they have these fields. Accepts `--top N` to limit rows. `--json` emits `{geographic_split: {...}, sector_split: {...}}` matching the `analysis` section schema. Instruments missing a split field emit a per-field warning and are excluded from that breakdown only.
- Positions with `target_weight_pct: null` are skipped with a stderr warning (securities-only portfolio.json from Stage 4, before weights are assigned).

## portfolio.json

- `positions[].instrument.top_holdings` must be populated by the security screener for overlap analysis to work. Missing top_holdings in an ETF prints a warning and excludes that ETF.
- `top_holdings[].weight_pct` is the holding's weight *within the ETF* (not portfolio-level). The scripts multiply by `target_weight_pct / 100` to get portfolio-level contribution.
