# CoFolio — Developer Notes

## Project Overview

CoFolio is an Agent Plugins-compatible portfolio advisor for Claude Cowork, ChatGPT Work, and Codex. It produces file-based state (Markdown + JSON) in the user's workspace directory, from investor profiling through to an actionable portfolio report with ongoing rebalancing.

## Technical Stack

- Python 3.10+ for analysis scripts (numpy, pandas, yfinance)
- Dependencies are prepared on demand by the portfolio-advisor skill with `uv` or an isolated virtual environment
- No build step — the plugin is Markdown skills and Python scripts

## Architecture

- **Portable manifest** (`plugins/cofolio/plugin.json`): Agent Plugins v1 manifest. The Codex-specific manifest is at `plugins/cofolio/.codex-plugin/plugin.json`; the Claude marketplace remains at `.claude-plugin/marketplace.json`.
- **Portfolio Advisor skill** (`plugins/cofolio/skills/portfolio-advisor/`): Single entry point — handles intent detection, pipeline state detection, stage routing, and `PORTFOLIO-CONTEXT.md` generation. `SKILL.md` is the main prompt; `references/` contains on-demand stage files.
- **Reference files** (`plugins/cofolio/skills/portfolio-advisor/references/`): One file per pipeline stage (`1-investor-profile.md` through `7-maintenance.md`) plus base prompts for macro research and security screening.
- **Analysis scripts** (`plugins/cofolio/skills/portfolio-advisor/scripts/`): Python analysis tools invoked by skills with `--json` for machine-readable output. Detailed below.
- **Pipeline files** (in user's workspace): `investor-profile.md`, `asset-allocation.md`, `macro-themes.md`, `portfolio.json`, `report.md` — both checkpoints and deliverables.

## Codebase Patterns

- Single skill (`portfolio-advisor`) handles all pipeline stages; stage-specific instructions and domain knowledge are loaded on demand from `references/N-stage-name.md` files.
- The portfolio-advisor skill generates `PORTFOLIO-CONTEXT.md` in the user's portfolio workspace to persist context across sessions.
- Specialist prompts are read before each delegated research task; subagents return data, while the skill handles pipeline-file writes.

## Scripts

- Analysis scripts and their `requirements.txt` live at `plugins/cofolio/skills/portfolio-advisor/`.
- All analysis scripts read `portfolio.json` from a path passed as a positional CLI argument (default: `portfolio.json` in CWD).
- Scripts accept `--json` to emit machine-readable output for skill consumption. The JSON format matches the `analysis` section schema in `portfolio.json` (see PRD Section 4 / Stage 5).
- `overlap.py`: position `type` field drives logic — `"etf"` decomposes `top_holdings`, `"stock"` counts directly at `target_weight_pct`. Other types (bonds, cash) are silently skipped.
- `fees.py`: computes weighted average TER and projects fee drag using monthly compounding. Accepts `--growth` (annual %), `--contribution` (monthly amount), `--initial` (starting value), `--horizons` (comma-separated years). Stocks/positions without `ter_pct` contribute 0 to the weighted TER. `--json` emits `{weighted_avg_ter_pct, fee_drag_10y, fee_drag_20y, fee_drag_30y}` (keys follow `fee_drag_<N>y` pattern for any horizons).
- `concentration.py`: computes blended geographic and sector breakdowns by weighting each instrument's `geographic_split` / `sector_split` by `target_weight_pct / 100`. Both ETFs and stocks contribute if they have these fields. Accepts `--top N` to limit rows. `--json` emits `{geographic_split: {...}, sector_split: {...}}` matching the `analysis` section schema. Instruments missing a split field emit a per-field warning and are excluded from that breakdown only.
- `drift.py`: computes per-position drift (current_weight_pct − target_weight_pct) and flags positions exceeding `--threshold` (default ±5%). Accepts `--current FILE` (JSON array `[{ticker, current_weight_pct}]` or object `{ticker: weight_pct}`) for externally supplied weights; falls back to reading `current_weight_pct` directly from each position in `portfolio.json`. Accepts `--value AMOUNT` for trade sizing in portfolio currency. `--json` emits `{threshold_pct, portfolio_value, positions: [...], flagged_count, flagged_positions}`. Positions missing `current_weight_pct` (from either source) emit a per-position warning and are excluded.
- `rebalance.py`: optimizes monthly contribution allocation to minimize drift without selling. Requires `--contribution AMOUNT` and `--value AMOUNT` (both mandatory). Accepts `--current FILE` (same format as `drift.py`). Accepts `--threshold PCT` (default 5.0) and `--timeframe MONTHS` (default 12) to control when sell suggestions are triggered. Even currently-overweight positions may receive some contribution when the contribution is large relative to portfolio size (because the denominator grows). `--json` emits `{contribution, portfolio_value, new_total, positions: [...], unallocated, fully_rebalanced, months_to_target, sell_suggestions}`.
- `prices.py`: fetches latest prices via yfinance for all tickers in portfolio.json. Reads `current_holdings` (share count) from each position to compute current values and weights. Handles ticker resolution for European exchanges via `--exchange-suffix` or automatic mapping from `instrument.exchange` (XETRA→`.DE`, Euronext Amsterdam→`.AS`, LSE→`.L`, etc.). `--json` emits `{as_of, positions: [...], failed_tickers, total_value, current_weights}`. The `current_weights` object is keyed by ticker and compatible with `drift.py --current` / `rebalance.py --current`. Positions without `current_holdings` still get prices fetched but have null values/weights. Requires `yfinance` (in requirements.txt).
- `dca.py`: simple DCA allocation calculator. Given `--contribution AMOUNT` and portfolio.json target weights, computes the ideal allocation per position (`amount = contribution * target_weight_pct / 100`). No drift awareness — for drift-correcting allocation, use `rebalance.py`. `--json` emits `{contribution, positions: [...], total_allocated, total_weight_pct}`.
- Positions with `target_weight_pct: null` are skipped with a stderr warning (securities-only portfolio.json from Stage 4, before weights are assigned).

## portfolio.json

- `positions[].instrument.top_holdings` must be populated by the security screener for overlap analysis to work. Missing top_holdings in an ETF prints a warning and excludes that ETF.
- `top_holdings[].weight_pct` is the holding's weight *within the ETF* (not portfolio-level). The scripts multiply by `target_weight_pct / 100` to get portfolio-level contribution.
