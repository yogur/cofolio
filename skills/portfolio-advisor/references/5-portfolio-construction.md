# Stage 5 — Portfolio Construction

## Instructions

You are running Stage 5 of the CoFolio portfolio pipeline — portfolio construction and analysis. Your job is to turn the list of selected securities (from Stage 4) into a fully weighted portfolio, run quantitative analysis, present the results so the user can make informed adjustments, and write the final `portfolio.json`.

The weight assignment methodology, script invocation details, analysis interpretation guidelines, and the updated portfolio.json schema (with the `analysis` section) are in the reference sections below.

## Context You May Receive

When invoked by the orchestrator or directly, you may receive:

- **Entry point:** Whether this is a sequential pipeline build or a re-entry to adjust weights
- **Investor profile context:** Key fields from `investor-profile.md` (monthly contribution, initial portfolio value, assumed growth rate, risk tolerance, experience level)
- **Allocation context:** Structure and bucket targets from `asset-allocation.md`

Use whatever context is available. If you don't receive explicit context, read the files yourself.

## How to Run This Stage

### 1. Gather context from upstream files

Read these files from the current working directory:

**`portfolio.json` (required):**
- List of positions with selected instruments (from Stage 4)
- Check that `target_weight_pct` is `null` for all positions — this confirms Stage 4 output that hasn't been weighted yet
- If positions already have weights and an `analysis` section, this is a re-entry (e.g., user wants to adjust weights). Treat existing weights as starting point rather than proposing from scratch.

**`asset-allocation.md` (required):**
- Portfolio structure (core/satellite, single-tier, etc.)
- Bucket-level targets (e.g., core = 55%, satellite = 45%)
- Sub-allocation within each bucket (e.g., core US 35%, core Europe 10%)
- Tactical tilt budget (how much satellite flexibility exists)

**`investor-profile.md` (needed for fee drag projection):**
- Monthly contribution amount — passed to `fees.py` via `--contribution`
- Current portfolio value (if known) — passed to `fees.py` via `--initial`
- Assumed growth rate — passed to `fees.py` via `--growth` (default to 7% if not specified)
- Time horizon — determines which fee drag horizons are most relevant
- Experience level — controls explanation depth

**`macro-themes.md` (optional, for hypothesis writing):**
- Selected themes and their theses — used to populate the `hypothesis` field for satellite positions

If `portfolio.json` doesn't exist, tell the user they need to complete security selection first (Stage 4). If `asset-allocation.md` doesn't exist, you can still propose weights but note that you're working without a target allocation framework.

### 2. Propose weights

Map each position to its allocation bucket and sub-allocation target, then propose a specific `target_weight_pct` for each position. The detailed methodology is in the reference sections below, but the core logic is:

1. **Start with bucket-level targets from `asset-allocation.md`.** If core = 55% and satellite = 45%, those are the envelopes.
2. **Within each bucket, distribute according to sub-allocation targets.** If core has US 35%, Europe 10%, EM 25%, Global ex-US 30% — and there's one instrument per slot — each gets that percentage of the core bucket.
3. **Convert bucket-relative weights to absolute portfolio weights.** If core is 55% and US is 35% of core, US absolute weight = 55% × 35% = 19.25%. Round to practical precision (0.5% increments are fine).
4. **For satellite positions with multiple instruments per theme,** split the theme's allocation among instruments based on conviction and diversification. For individual stocks, size them smaller than ETFs (higher idiosyncratic risk).
5. **Verify that all weights sum to 100%.** Adjust as needed — don't leave a gap or exceed 100%.

**Present the proposal clearly:**

Show a table with each position, its bucket, the proposed weight, and a brief rationale. Group by bucket.

> "Based on your 55/45 core-satellite allocation, here are the proposed weights:
>
> **Core (55% total):**
> | Position | Weight | Rationale |
> |----------|--------|-----------|
> | iShares Core S&P 500 (SXR8) | 19.25% | 35% of core bucket |
> | Vanguard FTSE All-World ex-US | 16.50% | 30% of core bucket |
> | ...
>
> **Satellite (45% total):**
> | Position | Weight | Rationale |
> |----------|--------|-----------|
> | VanEck Semiconductor ETF | 15.00% | Primary AI infrastructure exposure |
> | ASML (stock) | 5.00% | High-conviction single stock — sized smaller |
> | ...
>
> All weights sum to 100%. Shall I proceed with these, or would you like to adjust?"

Wait for user confirmation or adjustment before running analysis. Weight changes after analysis is expensive (re-running all scripts), so get alignment first.

### 3. Write hypothesis fields

For each position, write a brief `hypothesis` — the investment thesis explaining why this instrument is in the portfolio. This is especially important for satellite/thematic positions.

- **Core positions:** The hypothesis is typically about broad exposure: "Broad US large-cap exposure as portfolio anchor. Low-cost market-cap-weighted index provides diversified US equity beta."
- **Satellite positions:** Reference the macro theme: "Captures the AI infrastructure thesis — semiconductor equipment is a bottleneck in the AI buildout. ASML has near-monopoly on EUV lithography."
- **Keep hypotheses concise** — 1-2 sentences. They serve as a reminder of why the position exists, used during Stage 7 (maintenance) to evaluate whether the thesis still holds.

### 4. Apply weights to portfolio.json

Once the user confirms weights (with any adjustments), update `portfolio.json`:

- Set `target_weight_pct` for each position
- Set `hypothesis` for each position
- Update the `updated` date field

Do NOT write the `analysis` section yet — that comes after running the scripts. Write the file now so the scripts can read it.

### 5. Run the analysis scripts

Run all three analysis scripts against the updated `portfolio.json`. The scripts live in the skill's `scripts/` directory. Pass `--json` to each for machine-readable output.

**Overlap analysis:**
```bash
python scripts/overlap.py portfolio.json --top 10 --threshold 3.0 --json
```
This returns the top 10 single-stock exposures across all ETF holdings and stock positions.

**Fee drag analysis:**
```bash
python scripts/fees.py portfolio.json --growth <rate> --contribution <monthly> --initial <value> --horizons 10,20,30 --json
```
Extract `--growth`, `--contribution`, and `--initial` from `investor-profile.md`. If values aren't available, use sensible defaults (7% growth, 0 contribution, 0 initial) and note the assumptions.

**Concentration analysis:**
```bash
python scripts/concentration.py portfolio.json --json
```
This returns the blended geographic and sector breakdowns.

Run all three in parallel — they're independent.

See the Script Invocation Reference section below for the exact output format of each script and how to extract the values you need for the `analysis` section.

### 6. Present the analysis results

Present the analysis in a structured, readable format. The goal is to help the user understand where their money actually ends up — not just which instruments they own, but what underlying exposures they have.

**Overlap analysis — "Where your money actually is":**
- Show the top stock exposures table
- Flag any stock exceeding the threshold (default 3%) — explain what it means
- If a flagged stock appears through multiple instruments, show the breakdown (e.g., "NVIDIA: 1.2% via S&P 500 + 2.4% via Semiconductor ETF + 5.0% direct = 8.6% total")
- Context: Is this concentration intentional (user chose to overweight via satellite) or accidental (overlap between core ETFs)?

**Fee drag analysis — "What you'll pay over time":**
- Show weighted average TER
- Show fee drag projections at 10Y, 20Y, 30Y
- Context: Is the weighted TER low (< 0.15%), moderate (0.15-0.30%), or high (> 0.30%)? What's driving it — usually one or two expensive positions
- If there's a significantly cheaper alternative for the most expensive position, mention it (but don't push — just note the option)

**Concentration analysis — "Geographic and sector tilt":**
- Show geographic breakdown — where is the portfolio actually invested?
- Show sector breakdown — which sectors dominate?
- Context: Does the geographic breakdown match the user's allocation intent? Is there unintentional tech concentration (common with US heavy portfolios)?

**Adapt to experience level:**
- **Beginner:** Explain what overlap means, why fee drag matters over decades, and what geographic concentration implies. Use concrete examples.
- **Intermediate:** Focus on the implications and whether the numbers align with their intent. Skip definitions.
- **Experienced:** Lead with the data tables. They'll interpret the numbers.

### 7. Handle user adjustments

After presenting analysis, the user may want to adjust. Common scenarios:

- **"Too much overlap in X":** Suggest reducing the weight of the overlapping position, swapping to a less correlated alternative, or accepting the concentration as intentional
- **"Fees are too high":** Identify the most expensive position(s) and discuss cheaper alternatives. This may require re-invoking the security screener agent (suggest going back to Stage 4 for that instrument)
- **"Too concentrated in region/sector Y":** Suggest reweighting toward underrepresented areas, or note that the concentration matches their stated conviction
- **"Change weight of position Z to N%":** Apply the change, adjust other weights to maintain 100% total, and note which positions absorbed the difference
- **"Add/remove a position":** This requires going back to Stage 4 (security selection). Suggest it and explain why.

After any weight adjustment:
1. Update `portfolio.json` with new weights
2. Re-run all three analysis scripts (weights changed, so all analysis is invalidated)
3. Present the updated analysis
4. Ask if the user is satisfied

This loop continues until the user approves the final portfolio.

### 8. Write the analysis section

Once the user approves, add the `analysis` section to `portfolio.json`. See the Updated portfolio.json Schema section below for the exact schema. The analysis section captures the script outputs in a structured format:

```json
{
  "analysis": {
    "weighted_avg_ter_pct": 0.19,
    "fee_drag_10y": 2850,
    "fee_drag_20y": 12400,
    "fee_drag_30y": 28400,
    "top_stock_exposures": [
      { "ticker": "NVDA", "name": "NVIDIA", "total_pct": 4.8 },
      ...
    ],
    "geographic_split": { "US": 52, "Europe": 18, ... },
    "sector_split": { "Technology": 35, "Financials": 12, ... }
  }
}
```

Update the `updated` date field to today.

### 9. Summarize and hand off

After writing the final `portfolio.json`, tell the user:

- **Weight summary:** N positions totaling 100%, split across buckets
- **Key analysis highlights:** Weighted TER, top concentration risks, any flagged exposures
- **Data note:** Mention that the analysis is based on holdings data captured during security screening (Stage 4) and note the `data_as_of_date` — holdings shift over time
- **What comes next:**
  - **If part of a pipeline build:** "Next is report generation — I'll produce a comprehensive portfolio report covering your profile, strategy, holdings, and analysis."
  - **If standalone re-entry:** "Your portfolio weights and analysis have been updated. You may want to regenerate the report (Stage 6) to reflect the changes."

## Important Behaviors

- **Get weight confirmation before running analysis.** Scripts take effort and produce output the user needs to process. Don't waste a round by running analysis on weights the user hasn't approved. Ask first, analyze second.
- **Weights must sum to exactly 100%.** There's no "cash" position unless the user explicitly wants one. If rounding creates a small gap, absorb it in the largest position.
- **Re-run all scripts after any weight change.** Overlap, concentration, and fee drag all depend on weights. A change to one position's weight affects all three analyses. Don't present stale analysis.
- **Don't re-screen instruments.** This stage assigns weights and runs analysis on existing instruments. If the user wants to swap an instrument, that's Stage 4. You can suggest it, but don't invoke the security-screener agent yourself.
- **Individual stocks should be sized carefully.** A single stock carries more idiosyncratic risk than an ETF. Unless the user has strong conviction and understands the risk, keep individual stock positions smaller than ETF positions. A common guideline is 3-5% per stock versus 10-20% per ETF, but defer to the user's preference.
- **The analysis section uses script outputs directly.** Don't manually calculate overlap, fees, or concentration — use the scripts. They handle edge cases (missing data, null weights) consistently. You interpret and present the results.
- **Fee drag projections need investor profile data.** The fee drag numbers are much more meaningful with actual contribution amounts and initial values. If `investor-profile.md` has these, use them. If not, note the assumptions clearly.
- **Don't over-optimize.** A portfolio with 19.25% vs 19.5% in a position is not meaningfully different. Focus the user's attention on decisions that matter — large weight shifts, concentrated exposures, expensive positions — not cosmetic precision.

---

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

All scripts are in the skill's `scripts/` directory. They read `portfolio.json` from a path passed as a positional argument and accept `--json` for machine-readable output. Scripts only operate on positions that have `target_weight_pct` set — positions with `null` weights are skipped with a warning.

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
