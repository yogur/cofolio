# Portfolio Construction — Reference Material

This file contains the weight assignment methodology, script invocation details, output format specifications, analysis interpretation guidelines, and the updated `portfolio.json` schema with the `analysis` section. Read this when proposing weights, running scripts, or writing the final output.

---

## Weight Assignment Methodology

### Step 1: Extract Bucket Targets

From `asset-allocation.md`, extract:

- **Top-level split:** Percentages for each bucket (e.g., core 55%, satellite 45%)
- **Sub-allocation within core:** Per-region or per-style percentages (these are relative to the core bucket, not absolute)
- **Satellite structure:** Whether satellite has predefined sub-allocation or is allocated per-theme by conviction

### Step 2: Map Positions to Buckets

Each position in `portfolio.json` has a `bucket` field ("core" or "satellite") and a `slot` field. Match each position to its allocation target:

| Position Field | Maps To |
|---------------|---------|
| `bucket: "core"`, `slot: "US_blend"` | Core sub-allocation → US region target |
| `bucket: "core"`, `slot: "emerging_markets"` | Core sub-allocation → EM region target |
| `bucket: "satellite"`, `slot: "ai_infrastructure"` | Satellite budget → theme allocation |

### Step 3: Compute Absolute Weights

**For core positions** — the math is straightforward:

```
absolute_weight = bucket_pct × sub_allocation_pct / 100
```

Example: Core = 55%, US = 35% of core → US absolute weight = 55 × 35 / 100 = 19.25%

If `asset-allocation.md` specifies sub-allocations as percentages of the total portfolio rather than of the bucket, use those directly.

**For satellite positions** — allocation depends on the structure:

- **If satellite has predefined sub-allocation targets:** Same math as core
- **If satellite is allocated by conviction (common):** Distribute the satellite budget across themes based on confidence level and diversification:

| Factor | Higher Weight | Lower Weight |
|--------|-------------|-------------|
| Theme confidence | High confidence → larger allocation | Speculative → smaller allocation |
| Theme time horizon | Structural (multi-year) → larger | Cyclical/tactical → smaller |
| Instrument type | ETF (diversified) → can be larger | Individual stock → size down for risk |
| Number of satellite positions | Fewer positions → each gets more | Many positions → each gets less |

**Guideline ranges for satellite positions:**

| Instrument Type | Typical Range | Notes |
|----------------|--------------|-------|
| Thematic ETF (high confidence) | 8-15% of total portfolio | Diversified, can bear larger allocation |
| Thematic ETF (speculative) | 3-8% of total portfolio | Smaller due to uncertainty |
| Individual stock (high conviction) | 3-7% of total portfolio | Single-stock risk limits sizing |
| Individual stock (speculative) | 1-3% of total portfolio | Small experimental position |

These are starting points, not rules. The user's risk tolerance, experience, and stated preferences override these guidelines.

### Step 4: Round and Reconcile

- Round weights to practical precision: 0.5% increments or whole percentages are fine
- Verify all weights sum to exactly 100%
- If rounding creates a gap, add the remainder to the largest core position (it's the most liquid and least sensitive to small weight changes)
- If rounding creates an excess, trim from the largest core position

### Handling Edge Cases

**One instrument per slot (simple case):** The slot's weight equals the allocation target weight. Straightforward.

**Multiple instruments per slot:** Split the slot's allocation. For example, if the AI Infrastructure satellite has both a semiconductor ETF and an individual stock:
- Semiconductor ETF: 10% (bulk of the theme exposure)
- ASML stock: 5% (high-conviction single pick)
- Total for the theme: 15% of the satellite budget

**Slots with no allocation target:** If a position was added during Stage 4 that doesn't directly map to an `asset-allocation.md` target (e.g., user added a gold position ad hoc), discuss with the user where it fits and what weight it should have. It must come from somewhere — reduce another position to make room.

**Re-entry with existing weights:** If positions already have weights (user is adjusting), show current weights alongside proposed changes. Don't reset to zero and re-derive — treat the existing weights as the baseline.

---

## Script Invocation Reference

All scripts are in the plugin's `scripts/` directory. They read `portfolio.json` from a path passed as a positional argument and accept `--json` for machine-readable output. Scripts only operate on positions that have `target_weight_pct` set — positions with `null` weights are skipped with a warning.

### overlap.py

**Purpose:** Computes look-through single-stock exposure across all ETF positions and direct stock positions.

**Invocation:**
```bash
python scripts/overlap.py portfolio.json --top 10 --threshold 3.0 --json
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `portfolio.json` | `portfolio.json` | Path to portfolio file |
| `--top N` | 10 | Number of top exposures to return |
| `--threshold PCT` | 3.0 | Flag stocks exceeding this % of portfolio |
| `--json` | off | Output as JSON array |

**JSON output format:**
```json
[
  { "ticker": "AAPL", "name": "Apple", "total_pct": 3.92 },
  { "ticker": "MSFT", "name": "Microsoft", "total_pct": 3.71 },
  ...
]
```

**How it works:**
- For ETFs: multiplies each top holding's weight within the ETF by the position's `target_weight_pct / 100` to get portfolio-level contribution
- For stocks: counts the position's `target_weight_pct` directly as the stock's portfolio-level exposure
- Aggregates across all positions — the same stock appearing in multiple ETFs has its contributions summed
- Sorts by total exposure descending, returns top N

**What to extract for `analysis.top_stock_exposures`:** Use the JSON output directly — it's already in the right format.

### fees.py

**Purpose:** Computes weighted average TER and projects cumulative fee drag over time.

**Invocation:**
```bash
python scripts/fees.py portfolio.json --growth 7.0 --contribution 3500 --initial 0 --horizons 10,20,30 --json
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `portfolio.json` | `portfolio.json` | Path to portfolio file |
| `--growth RATE` | 7.0 | Assumed annual growth rate (%) |
| `--contribution AMT` | 0 | Monthly contribution in portfolio currency |
| `--initial AMT` | 0 | Current portfolio value |
| `--horizons YEARS` | 10,20,30 | Comma-separated projection years |
| `--json` | off | Output as JSON object |

**Where to get argument values from `investor-profile.md`:**
| Argument | Profile Field | Fallback |
|----------|-------------|----------|
| `--contribution` | Monthly amount under "Contributions" | 0 |
| `--initial` | Not always in profile (new portfolios start at 0) | 0 |
| `--growth` | Not in profile — use 7% as a standard long-term equity return assumption | 7.0 |
| `--horizons` | Derive from time horizon — include horizons up to the user's stated horizon | 10,20,30 |

**JSON output format:**
```json
{
  "weighted_avg_ter_pct": 0.1912,
  "fee_drag_10y": 2850.42,
  "fee_drag_20y": 12400.18,
  "fee_drag_30y": 28400.55
}
```

The `fee_drag_Ny` keys follow the pattern `fee_drag_<horizon>y` and represent the cumulative currency amount lost to fees over that period compared to a zero-fee portfolio with the same growth rate.

**What to extract for the `analysis` section:**
- `weighted_avg_ter_pct` → `analysis.weighted_avg_ter_pct`
- `fee_drag_10y` → `analysis.fee_drag_10y`
- `fee_drag_20y` → `analysis.fee_drag_20y`
- `fee_drag_30y` → `analysis.fee_drag_30y`

Round fee drag values to whole numbers (they're currency amounts).

### concentration.py

**Purpose:** Computes blended geographic and sector concentration from per-instrument splits weighted by position weights.

**Invocation:**
```bash
python scripts/concentration.py portfolio.json --json
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `portfolio.json` | `portfolio.json` | Path to portfolio file |
| `--top N` | all | Limit rows per breakdown |
| `--json` | off | Output as JSON object |

**JSON output format:**
```json
{
  "geographic_split": {
    "US": 52.3,
    "Europe": 18.1,
    "Emerging Markets": 14.7,
    "Asia Developed": 10.2,
    "Other": 4.7
  },
  "sector_split": {
    "Technology": 34.8,
    "Financials": 12.1,
    "Healthcare": 10.3,
    "Industrials": 9.8,
    "Consumer Discretionary": 8.2,
    "Other": 24.8
  }
}
```

**How it works:**
- For each position, multiplies the instrument's `geographic_split` and `sector_split` percentages by `target_weight_pct / 100`
- Both ETFs and individual stocks contribute if they have these fields
- Instruments missing a split field are excluded from that breakdown only (with a warning)

**What to extract for the `analysis` section:**
- `geographic_split` → `analysis.geographic_split`
- `sector_split` → `analysis.sector_split`

Round values to whole numbers for the analysis section (e.g., 52 not 52.3) for readability.

---

## Analysis Interpretation Guidelines

Use these when presenting script results to the user. The goal is to translate numbers into actionable insight, not just report data.

### Overlap Interpretation

| Situation | What It Means | Suggested Action |
|-----------|--------------|-----------------|
| No stock exceeds 3% | Well-diversified single-stock exposure | No action needed — note this positively |
| 1-2 stocks at 3-5% | Mild concentration, likely intentional | Flag it, explain the source, confirm it's intentional |
| A stock exceeds 5% | Significant single-stock risk | Explain that 5%+ in one company means the portfolio's performance is meaningfully tied to that stock. Ask if this is intended. |
| A stock exceeds 8% | Very high concentration | Strongly note the risk. This usually happens when a stock appears in multiple ETFs AND as a direct position. Walk through the sources. |

**Common overlap patterns to call out:**

- **FAANG concentration via US + tech ETFs:** S&P 500 + NASDAQ 100 creates heavy overlap in Apple, Microsoft, NVIDIA, Amazon, Meta. Combined exposure to these 5 stocks can reach 20-30% of the portfolio.
- **Regional ETF overlap:** MSCI World is ~60% US. Holding both MSCI World and S&P 500 creates near-double US exposure.
- **Direct stock + ETF overlap:** Adding NVDA as a direct position when it's already 6% of the S&P 500 ETF creates stacking. The user should know their true NVDA exposure.

### Fee Drag Interpretation

| Weighted TER | Assessment | Context |
|-------------|-----------|---------|
| < 0.10% | Excellent | Core-only index portfolios achieve this |
| 0.10 - 0.20% | Good | Typical for diversified portfolios with some thematic ETFs |
| 0.20 - 0.35% | Moderate | Thematic/satellite ETFs are driving cost up |
| 0.35 - 0.50% | High | Consider whether expensive positions justify their cost |
| > 0.50% | Very high | Unusual for passive ETF portfolios — flag prominently |

**Presenting fee drag in perspective:**
- Always show the actual currency amount — "0.19% weighted TER costs you approximately EUR 28,400 over 30 years" is more impactful than just the percentage
- Compare to a lower-cost scenario — "If you swapped the 0.35% semiconductor ETF for a broader 0.12% tech ETF, your 30Y fee drag would drop by ~EUR 8,000"
- Note that fee drag is a projection, not a guarantee — it depends on the growth rate assumption

### Concentration Interpretation

**Geographic:**

| Pattern | What to Flag |
|---------|-------------|
| US > 60% | Heavy US tilt — common and often intentional, but note it |
| Any single region > 70% | Very concentrated — the portfolio's fortunes are tied to one region's economy |
| EM > 25% | Higher volatility exposure — ensure this matches risk tolerance |
| Europe < 10% with a European investor | Home bias in reverse — they may want some home exposure for currency alignment |

**Sector:**

| Pattern | What to Flag |
|---------|-------------|
| Technology > 35% | Heavy tech tilt — very common with US-heavy portfolios + tech satellites |
| Any sector > 40% | Significant sector concentration — if tech corrects 30%, the portfolio takes a ~12%+ hit |
| Top 2 sectors > 50% | Moderately concentrated — flag if unintentional |
| Good diversification | No sector above 25%, top 5 sectors are spread — note this positively |

---

## Updated portfolio.json Schema

This is the full schema for the output of Stage 5. It extends the Stage 4 schema by filling in `target_weight_pct`, `hypothesis`, and adding the `analysis` section.

```json
{
  "version": "1.0",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "positions": [
    {
      "bucket": "core | satellite",
      "slot": "descriptive_slot_name",
      "instrument": {
        "...same as Stage 4 output — do not modify instrument data..."
      },
      "target_weight_pct": 19.25,
      "current_holdings": null,
      "hypothesis": "Brief investment thesis for this position",
      "theme_ids": ["theme_id_snake_case"]
    }
  ],
  "watchlist": [
    {
      "...same as Stage 4 output..."
    }
  ],
  "analysis": {
    "weighted_avg_ter_pct": 0.19,
    "fee_drag_10y": 2850,
    "fee_drag_20y": 12400,
    "fee_drag_30y": 28400,
    "top_stock_exposures": [
      { "ticker": "NVDA", "name": "NVIDIA", "total_pct": 4.8 },
      { "ticker": "AAPL", "name": "Apple", "total_pct": 3.9 },
      { "ticker": "MSFT", "name": "Microsoft", "total_pct": 3.7 }
    ],
    "geographic_split": {
      "US": 52,
      "Europe": 18,
      "Emerging Markets": 15,
      "Asia Developed": 10,
      "Other": 5
    },
    "sector_split": {
      "Technology": 35,
      "Financials": 12,
      "Healthcare": 10,
      "Industrials": 10,
      "Consumer Discretionary": 8,
      "Other": 25
    }
  }
}
```

### Schema Notes

- **Do not modify `instrument` data.** The instrument fields (name, ISIN, top_holdings, geographic_split, sector_split, etc.) were collected by the screener agent in Stage 4. Don't change them here — you're only adding weights and analysis.
- **`target_weight_pct`:** A number (not null). Must be > 0 for all positions. All values must sum to exactly 100.
- **`hypothesis`:** A string (not null). 1-2 sentences explaining why this instrument is in the portfolio. For core positions, reference broad exposure goals. For satellite positions, reference the macro theme.
- **`current_holdings`:** Remains `null` for new portfolios. Populated in Stage 7 (maintenance) with actual holding data.
- **`analysis` section:** Added at the top level of the JSON, alongside `positions` and `watchlist`. All values come from script outputs — don't compute them manually.
- **`fee_drag_Ny` keys:** Follow the pattern `fee_drag_<horizon>y`. Use integer values (round to whole numbers — they represent currency amounts).
- **`top_stock_exposures`:** Include the top 5-10 stocks from the overlap analysis. Each entry has `ticker`, `name`, and `total_pct` (round to 1 decimal place).
- **`geographic_split` and `sector_split` in analysis:** Round to whole numbers. These are portfolio-level blended values, not per-instrument values.
- **`watchlist`:** Preserved from Stage 4 output without modification.

---

## Adjustment Workflow Reference

When the user requests a weight change, follow this sequence:

1. **Validate the request:** Does the change make sense? If the user wants 50% in a single stock, note the risk but don't refuse — it's their portfolio.
2. **Apply the change:** Update the target position's weight.
3. **Rebalance remaining positions:** The total must stay at 100%. Proportionally scale other positions in the same bucket, or ask the user which positions should absorb the difference.
4. **Show the before/after:** Present a comparison table showing old weights → new weights for all affected positions.
5. **Re-run all three scripts:** All analysis depends on weights.
6. **Present updated analysis:** Highlight what changed — "Your tech concentration went from 35% to 42% after increasing the semiconductor ETF weight."
7. **Confirm again:** "Does this look right, or would you like to adjust further?"

This loop repeats until the user says they're satisfied.
