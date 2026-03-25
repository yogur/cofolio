---
name: portfolio-construction
description: "Assigns final weights to all selected securities in portfolio.json, then runs overlap, fee drag, and concentration analysis scripts to produce a complete portfolio specification. Reads portfolio.json (securities without weights from Stage 4) and asset-allocation.md (target percentages), proposes position-level weights that map to the allocation targets, invokes scripts/overlap.py, scripts/fees.py, and scripts/concentration.py to analyze the assembled portfolio, presents all results to the user for review and adjustment, and writes the final portfolio.json with weights and an analysis section. Use this skill whenever Stage 5 of the portfolio pipeline is active, the user wants to assign or revise portfolio weights, the user wants to run portfolio analysis, or the orchestrator routes here."
---

# Portfolio Construction Skill

You are running Stage 5 of the CoFolio portfolio pipeline — portfolio construction and analysis. Your job is to turn the list of selected securities (from Stage 4) into a fully weighted portfolio, run quantitative analysis, present the results so the user can make informed adjustments, and write the final `portfolio.json`.

The weight assignment methodology, script invocation details, analysis interpretation guidelines, and the updated portfolio.json schema (with the `analysis` section) are in `reference.md` next to this file. Read it before starting.

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

Map each position to its allocation bucket and sub-allocation target, then propose a specific `target_weight_pct` for each position. The detailed methodology is in `reference.md`, but the core logic is:

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

Run all three analysis scripts against the updated `portfolio.json`. The scripts live in the plugin's `scripts/` directory. Pass `--json` to each for machine-readable output.

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

See `reference.md` for the exact output format of each script and how to extract the values you need for the `analysis` section.

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

Once the user approves, add the `analysis` section to `portfolio.json`. See `reference.md` for the exact schema. The analysis section captures the script outputs in a structured format:

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

## After This Stage Completes

Once the output file is written, generate or update `CLAUDE.md` in the project root following the orchestrator's CLAUDE.md Generation instructions. Read whichever pipeline files exist and assemble the context file so a fresh session has full context.
