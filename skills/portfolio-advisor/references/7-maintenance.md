# Stage 7 — Maintenance

## Instructions

You are running Stage 7 of the CoFolio portfolio pipeline — ongoing maintenance and rebalancing. Your job is to take an existing portfolio, figure out what data is stale or missing, collect only what's needed, run drift and rebalancing analysis, validate that the investment theses still make sense, and produce an actionable maintenance report.

The detailed reference material — script invocation, staleness criteria, hypothesis validation checklist, and maintenance report template — is in the reference sections below.

## Context You May Receive

When invoked by the orchestrator or `/portfolio-advisor` for rebalancing, you may receive:

- **Entry point:** Whether this is a `/portfolio-advisor` rebalance request, a direct request, or an orchestrator hand-off
- **Investor profile highlights:** Key fields from `investor-profile.md`
- **Portfolio summary:** Position count and structure from `portfolio.json`
- **Pipeline file inventory:** Which files exist and their approximate ages

Use whatever context is available. If you don't receive explicit context, read the files yourself.

## How to Run This Stage

### 1. Read pipeline state and assess data freshness

Read all pipeline files from the current working directory:

**`portfolio.json` (required):**
- All positions with target weights, instruments, hypotheses, and the `analysis` section
- Check `data_as_of_date` on each instrument — how old is the holdings data?
- Check the `updated` date on the portfolio itself

**`investor-profile.md` (required for contribution optimization):**
- Monthly contribution amount — needed for `rebalance.py --contribution`
- Risk tolerance, experience level — controls explanation depth and threshold sensitivity
- Brokerage and currency — for actionable trade instructions

**`macro-themes.md` (check freshness):**
- Research date — if older than 30 days, flag as stale
- Selected themes and their invalidation triggers — used for hypothesis validation

**`asset-allocation.md` (context):**
- Target allocation structure — useful for interpreting whether drift is structural or tactical
- Bucket targets — reference point for weight decisions

**`report.md` (optional):**
- The last report — note when it was generated

Present a brief state summary to the user:

> "Here's what I see in your portfolio workspace:
> - **Portfolio:** N positions, last updated [date]
> - **Macro research:** Conducted [date] — [fresh/stale]
> - **Instrument data:** As of [date] — [fresh/stale]
> - **Last report:** Generated [date]
>
> To run drift analysis, I need your current portfolio weights. Do you have updated weights or current values to share?"

### 2. Collect current weights

Drift analysis requires knowing where the portfolio actually stands today, not just where the targets are. Current weights can come from:

**Option A — User provides a current weights file:**
The user supplies a JSON file with current weights. Accept either format:
- Array: `[{"ticker": "SXR8", "current_weight_pct": 22.1}, ...]`
- Object: `{"SXR8": 22.1, "VXUS": 15.3, ...}`

Save this as `current_weights.json` in the working directory for the scripts to consume.

**Option B — User provides current values:**
The user tells you the current value of each position (e.g., from their brokerage account). Compute weights from values:
- `current_weight_pct = position_value / total_portfolio_value * 100`
- Write the computed weights to `current_weights.json`

**Option C — User provides total portfolio value only:**
If the user can only provide the total portfolio value and no per-position data, you cannot run drift analysis. Explain this clearly and suggest they check their brokerage for position-level values. You can still proceed with hypothesis validation and macro refresh without current weights.

**Option D — Weights already in portfolio.json:**
If positions have `current_weight_pct` fields populated (from a previous maintenance run), you can use those — but note the date they were captured and ask if they're still accurate.

Also ask for the **total portfolio value** — this is needed by both `drift.py --value` and `rebalance.py --value` for trade sizing.

### 3. Run drift analysis

Once you have current weights and portfolio value, run the drift analysis script:

```bash
python scripts/drift.py portfolio.json --current current_weights.json --threshold 5.0 --value <PORTFOLIO_VALUE> --json
```

See the reference sections below for output format and interpretation guidelines.

Present the drift results clearly:

- Show all positions with target, current, and drift
- Flag positions exceeding the threshold
- For flagged positions, note whether they need buying or selling
- If trade amounts are available, show them

Ask the user: "Would you like me to optimize your monthly contribution to address this drift, or would you prefer to adjust targets first?"

### 4. Run contribution optimization

If the user wants to proceed with rebalancing via contributions (the default and preferred approach), run the optimizer:

```bash
python scripts/rebalance.py portfolio.json --current current_weights.json --contribution <MONTHLY_CONTRIBUTION> --value <PORTFOLIO_VALUE> --threshold 5.0 --timeframe 12 --json
```

Extract `--contribution` from `investor-profile.md`. Extract `--value` from the user-provided portfolio value.

Present the optimization results:

- How much to allocate to each position this month
- Whether full rebalance is achievable in one contribution cycle
- Estimated months to fully rebalance (if not achievable immediately)
- Any sell suggestions (only if drift can't be corrected within the timeframe)

See the reference sections below for detailed presentation guidelines.

### 5. Validate investment hypotheses

This is what distinguishes maintenance from a simple rebalancing calculator. For each position, check whether the original investment thesis (the `hypothesis` field) still holds.

**For satellite/thematic positions — check theme validity:**

Read the invalidation triggers from `macro-themes.md` for each theme the position is linked to (via `theme_ids`). Ask:
- Has the thesis materially changed since the last research date?
- Have any invalidation triggers fired?
- Is there new information that strengthens or weakens the thesis?

If you have web access, briefly research the current state of each theme. If macro themes are stale (>30 days old), recommend a full macro refresh via `/portfolio-advisor`.

**For core positions — lighter check:**
Core positions are structural and change less frequently. Check:
- Has the instrument's TER changed significantly?
- Is there a materially better alternative now?
- Has the index methodology changed?

These checks usually pass. Don't belabor them unless something has genuinely changed.

**Present findings concisely:**

> "**Hypothesis check:**
> - AI Infrastructure (SMH, ASML): Thesis intact — AI capex spending continues to accelerate. No invalidation triggers fired.
> - European Defense (EDEF): Thesis intact — EU defense spending on track. Monitor: upcoming NATO summit in [month].
> - Core positions: No material changes to flag.
>
> Macro research was conducted [N days ago]. [Recommend refresh if >30 days / Themes still current if recent.]"

If a thesis is invalidated or weakened, discuss with the user before proceeding. Options include:
- Reduce the position's weight
- Replace the instrument (triggers a security screening subagent)
- Remove the position and redistribute weight
- Keep the position but note the increased risk

### 6. Re-run portfolio analysis (if weights changed)

If the maintenance process results in target weight changes (user adjusts weights based on drift analysis or hypothesis review), re-run the analysis scripts to update the `analysis` section:

```bash
python scripts/overlap.py portfolio.json --top 10 --threshold 3.0 --json
python scripts/fees.py portfolio.json --growth <rate> --contribution <monthly> --initial <portfolio_value> --horizons 10,20,30 --json
python scripts/concentration.py portfolio.json --json
```

Update the `analysis` section in `portfolio.json` with fresh results.

If target weights haven't changed (just rebalancing contributions toward existing targets), skip re-running analysis — the existing analysis section is still valid since it's based on target weights, not current weights.

### 7. Update portfolio.json

After completing the maintenance review:

- Update `current_weight_pct` for each position (from the user-provided data)
- Update the `updated` date field to today
- If target weights were modified, update `target_weight_pct` and the `analysis` section
- If hypotheses were revised, update `hypothesis` fields

### 8. Generate maintenance report

Produce an updated `report.md` focused on the maintenance context. The report should follow the same 8-section structure as the initial report (see the Maintenance Report Adjustments section below) but with a maintenance focus:

- **Executive Summary:** Lead with what changed — drift status, key actions, any thesis updates
- **Action Plan:** This is the most important section for maintenance. Show the specific contribution allocation for this month, any sell orders if recommended, and the timeline to full rebalance
- **Macro Landscape:** Note any theme changes or staleness. If themes were refreshed, reflect the new research.
- **Risk Factors:** Update with any new risks identified during hypothesis validation

Read the `references/6-report-generation.md` file for the report structure and section guidance if needed, or write it directly if the maintenance changes are minor and a full report regeneration isn't warranted. Use your judgment — if only drift and contribution allocation changed, a focused update is better than regenerating the entire report.

### 9. Summarize and close

After completing the maintenance cycle:

- Summarize the key actions: what to buy this month, any position changes, any items to monitor
- Note when the next maintenance review should happen (suggest monthly, or sooner if themes are stale or drift is significant)
- Remind the user they can run `/portfolio-advisor` anytime to trigger another maintenance cycle
- If `CLAUDE.md` needs updating to reflect the new state, note that

## Important Behaviors

- **Don't re-ask what's already answered.** The investor profile, allocation targets, and macro themes are already captured. Read them — don't interview the user again. Only ask for what's genuinely missing: current weights and portfolio value.
- **Current weights are the bottleneck.** Without current weights, you can't run drift analysis or rebalancing optimization. Be clear about what you need and why. If the user can't provide weights, still offer value through hypothesis validation and macro freshness assessment.
- **Contributions first, selling last.** The rebalancing philosophy is to use monthly contributions to gradually correct drift. Selling is a last resort — only suggest it when `rebalance.py` indicates drift can't be corrected within the timeframe via contributions alone.
- **Don't blindly rebalance.** Before optimizing contributions, validate that the targets are still correct. If a thesis is invalidated, the target weight should change — rebalancing toward an obsolete target is worse than doing nothing.
- **Adapt to what changed.** If drift is minimal and theses are intact, say so and keep the review brief. Don't manufacture work. If drift is significant or a thesis has weakened, dig deeper.
- **Stale data is a risk.** Flag data freshness prominently. Instrument holdings data from 6 months ago may not reflect current ETF compositions. Macro research from 2 months ago may miss important developments. Be transparent about what you're working with.
- **Use the scripts.** Don't manually compute drift or rebalancing allocations — the scripts handle edge cases. You interpret and present the results.
- **The user's brokerage constrains execution.** Any buy/sell recommendations must be executable on the user's platform (from `investor-profile.md`). Include tickers, exchanges, and amounts.

---

# Maintenance — Reference Material

This file contains detailed script invocation reference, staleness criteria, hypothesis validation checklist, current weight collection guidance, and the maintenance report template. Read this when running the Stage 7 maintenance workflow.

---

## Data Freshness Criteria

Use these thresholds to determine what needs refreshing:

| Data Source | Fresh | Aging | Stale | Action When Stale |
|-------------|-------|-------|-------|-------------------|
| Macro themes (`macro-themes.md`) | < 14 days | 14–30 days | > 30 days | Recommend `/portfolio-advisor` to refresh |
| Instrument holdings data (`data_as_of_date`) | < 30 days | 30–90 days | > 90 days | Note in report; suggest re-screening if critical positions affected |
| Valuation snapshots (`valuation_snapshot.as_of_date`) | < 7 days | 7–30 days | > 30 days | Research current valuations for flagged stocks |
| Portfolio weights (`portfolio.json` `updated`) | < 7 days | 7–30 days | > 30 days | Ask user for current weights |
| Investor profile (`investor-profile.md`) | < 6 months | 6–12 months | > 12 months | Ask if anything has changed (contribution amount, risk tolerance, goals) |

When presenting freshness to the user, use plain language:

- **Fresh:** "Your macro research from [date] is current."
- **Aging:** "Your macro research is [N] days old — still usable but consider refreshing soon."
- **Stale:** "Your macro research from [date] is over 30 days old. Themes may have shifted — I'd recommend running `/portfolio-advisor` to update."

---

## Current Weight Collection

### What You Need

Two pieces of data from the user:

1. **Total portfolio value** — a single number in the portfolio currency
2. **Per-position current weights or values** — either as percentages or currency amounts

### How to Ask

Adapt your request to the user's experience level:

**For beginners:**
> "To see how your portfolio has drifted from its targets, I need to know where things stand today. Can you check your brokerage account and tell me:
> 1. Your total portfolio value (the number on your dashboard)
> 2. The current value of each position (or the percentage each position represents)
>
> If your brokerage shows a pie chart with percentages, those work perfectly. Otherwise, the euro amounts for each position are fine — I'll calculate the percentages."

**For intermediate/experienced:**
> "I need current weights for drift analysis. You can provide either:
> - A JSON file with `{ticker: weight_pct}` (or array format)
> - Position values, and I'll compute weights
> - A screenshot or paste of your brokerage breakdown
>
> Also need your total portfolio value for trade sizing."

### Computing Weights from Values

If the user provides position values instead of percentages:

```
current_weight_pct = (position_value / total_portfolio_value) * 100
```

Round to 2 decimal places. Verify the computed weights sum to approximately 100% (allow ±1% for rounding and cash balances). If there's a meaningful gap, ask if the user has a cash position or positions not in `portfolio.json`.

### Writing current_weights.json

After collecting weights (however provided), write a `current_weights.json` file in the working directory for the scripts to consume. Use the object format for simplicity:

```json
{
  "SXR8": 22.1,
  "VXUS": 14.8,
  "IS3N": 12.5,
  "SMH": 18.3,
  "ASML": 6.2,
  "EDEF": 11.4,
  "IMEU": 5.1,
  "IS3N": 9.6
}
```

Use instrument tickers from `portfolio.json` as keys. The scripts match by ticker first, then by name.

---

## Script Invocation Reference

The scripts live in the skill's `scripts/` directory (next to this file).

### drift.py

**Purpose:** Compare current weights against target weights, flag drifted positions, compute trade amounts.

**Invocation:**
```bash
python scripts/drift.py portfolio.json --current current_weights.json --threshold 5.0 --value <PORTFOLIO_VALUE> --json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `portfolio.json` | Yes | `portfolio.json` | Path to portfolio file |
| `--current FILE` | Recommended | reads from portfolio.json | JSON file with current weights |
| `--threshold PCT` | No | 5.0 | Drift threshold to flag positions (percentage points) |
| `--value AMOUNT` | Recommended | None | Portfolio value for trade sizing |
| `--json` | Yes (for skill) | off | Machine-readable output |

**JSON output:**
```json
{
  "threshold_pct": 5.0,
  "portfolio_value": 50000.00,
  "positions": [
    {
      "name": "VanEck Semiconductor ETF",
      "ticker": "SMH",
      "target_pct": 15.0,
      "current_pct": 18.3,
      "drift_pct": 3.3,
      "drift_abs": 3.3,
      "flagged": false,
      "action": "sell",
      "trade_pct": 3.3,
      "trade_amount": 1650.00
    }
  ],
  "flagged_count": 1,
  "flagged_positions": ["IS3N"]
}
```

**Key fields:**
- `drift_pct`: Positive means overweight, negative means underweight
- `flagged`: True if `drift_abs >= threshold`
- `action`: "buy" (underweight), "sell" (overweight), or "hold" (exact)
- `trade_amount`: Currency amount to trade (only if `--value` provided)

### rebalance.py

**Purpose:** Optimize monthly contribution allocation to minimize drift without selling.

**Invocation:**
```bash
python scripts/rebalance.py portfolio.json --current current_weights.json --contribution <MONTHLY> --value <PORTFOLIO_VALUE> --threshold 5.0 --timeframe 12 --json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `portfolio.json` | Yes | `portfolio.json` | Path to portfolio file |
| `--current FILE` | Recommended | reads from portfolio.json | JSON file with current weights |
| `--contribution AMT` | **Yes** | — | Monthly contribution in portfolio currency |
| `--value AMOUNT` | **Yes** | — | Current portfolio value |
| `--threshold PCT` | No | 5.0 | Drift threshold for sell suggestions |
| `--timeframe MONTHS` | No | 12 | Months before selling is suggested |
| `--json` | Yes (for skill) | off | Machine-readable output |

**Where to get argument values:**

| Argument | Source | Fallback |
|----------|--------|----------|
| `--contribution` | `investor-profile.md` → Monthly amount | Ask user |
| `--value` | User-provided total portfolio value | Ask user (required) |
| `--threshold` | User preference or default | 5.0 |
| `--timeframe` | User preference or default | 12 |

**JSON output:**
```json
{
  "contribution": 3500.00,
  "portfolio_value": 50000.00,
  "new_total": 53500.00,
  "positions": [
    {
      "name": "VanEck Semiconductor ETF",
      "ticker": "SMH",
      "target_pct": 15.0,
      "current_pct": 18.3,
      "drift_pct": 3.3,
      "current_value": 9150.00,
      "new_target_value": 8025.00,
      "buy_needed": 0.00,
      "allocation": 0.00,
      "post_pct": 17.1,
      "post_drift_pct": 2.1,
      "allocation_pct": 0.0
    }
  ],
  "unallocated": 0.00,
  "fully_rebalanced": false,
  "months_to_target": 4.2,
  "sell_suggestions": []
}
```

**Key fields:**
- `allocation`: Currency amount to buy this month for this position
- `allocation_pct`: What percentage of this month's contribution goes to this position
- `post_pct` / `post_drift_pct`: Projected weight and drift after this month's contribution
- `fully_rebalanced`: Whether one month's contribution fully corrects all drift
- `months_to_target`: Estimated months to fully rebalance via contributions (null if already rebalanced)
- `sell_suggestions`: Only populated when drift can't be corrected within `--timeframe` months

### Portfolio Analysis Scripts (for re-analysis after weight changes)

Only re-run these if target weights changed during maintenance. If you're just rebalancing contributions toward existing targets, skip — the existing `analysis` section in `portfolio.json` remains valid.

**Overlap:**
```bash
python scripts/overlap.py portfolio.json --top 10 --threshold 3.0 --json
```

**Fees:**
```bash
python scripts/fees.py portfolio.json --growth <rate> --contribution <monthly> --initial <portfolio_value> --horizons 10,20,30 --json
```
Note: For maintenance, use the current portfolio value as `--initial` (not 0 as for a new portfolio).

**Concentration:**
```bash
python scripts/concentration.py portfolio.json --json
```

---

## Drift Interpretation Guidelines

| Drift Level | Assessment | Suggested Action |
|-------------|-----------|-----------------|
| All positions within ±2% | Minimal drift | Note positively. No urgent action needed. Contributions can follow target weights directly. |
| Some positions at ±2–5% | Moderate drift | Normal market movement. Tilt contributions toward underweight positions per rebalance.py output. |
| Any position beyond ±5% | Significant drift | Flag prominently. This position has moved meaningfully from target. Discuss whether it's market-driven or thesis-driven before rebalancing. |
| Multiple positions beyond ±5% | Major drift | The portfolio has shifted significantly. Full rebalancing review warranted. Check if targets themselves need updating. |

### Context Matters

Before recommending rebalancing, consider:

- **Is the drift in the right direction?** If an overweight position is a high-conviction satellite bet that has performed well, the user may want to let it run. Present the data, not just the prescription.
- **Is the drift from market movement or from selective buying?** If the user has been buying only certain positions (e.g., fractional share purchases of a favorite stock), the drift is behavioral, not market-driven.
- **Tax implications:** Selling to rebalance triggers capital gains tax. For German investors (Abgeltungssteuer 26.375%), a €1,000 gain on a sell creates ~€264 in tax. Note this when sell suggestions come up.

---

## Hypothesis Validation Checklist

### For Each Satellite/Thematic Position

Walk through these questions using the position's `hypothesis` field and the corresponding theme from `macro-themes.md`:

1. **Is the core thesis still intact?**
   - What was the original investment rationale?
   - Has anything fundamentally changed?
   - Check the theme's invalidation triggers — have any been met?

2. **What's happened since the last review?**
   - If you have web access, briefly research: major news, earnings, sector developments
   - Has the theme's confidence level changed? (High → Medium? Speculative → invalidated?)

3. **Is the position still the best expression of the thesis?**
   - Has a better or cheaper instrument become available?
   - Has the instrument's tracking error, TER, or AUM changed materially?

4. **Does the position size still match conviction?**
   - If the thesis has strengthened, should the weight increase?
   - If the thesis has weakened (but not invalidated), should the weight decrease?
   - Is the position's drift in a direction consistent with the thesis?

### For Core Positions

Core positions change less often. Quick check:

1. **Is the instrument still competitive?** (TER, AUM, tracking error vs. alternatives)
2. **Has the index methodology changed?** (Rare, but worth noting if it has)
3. **Does the geographic/style exposure still match the allocation target?**

### Reporting Hypothesis Findings

For each position, report one of:

- **Thesis intact:** Brief note confirming no material changes. One line is enough.
- **Thesis strengthened:** Note what's improved and whether weight adjustment is warranted.
- **Thesis weakened:** Explain what changed, reference the invalidation trigger, and discuss options (reduce weight, swap instrument, remove position).
- **Thesis invalidated:** Clear recommendation to exit or significantly reduce the position. Explain what triggered the invalidation.

---

## Maintenance Report Adjustments

When generating or updating `report.md` after a maintenance cycle, adjust the standard report template (from `references/6-report-generation.md`) as follows:

### Executive Summary — Maintenance Focus

Lead with changes since last report:

```markdown
## 1. Executive Summary

*Maintenance review as of YYYY-MM-DD. Previous report: YYYY-MM-DD.*

Portfolio value: €XX,XXX across N positions. Since the last review:
- **Drift:** [N] position(s) have drifted beyond ±5%. [Brief description of largest drifts.]
- **Themes:** [All theses remain intact / Theme X has weakened — see below.]
- **Action:** This month, allocate €X,XXX contribution as detailed in the Action Plan.
  [If sells recommended: Additionally, consider selling €X of [position] to correct persistent overweight.]
```

### Action Plan — Contribution Allocation

This is the most critical section for a maintenance report. Replace the "Initial Purchase Order" with the rebalancing optimization output:

```markdown
## 6. Action Plan

### This Month's Contribution Allocation

Based on your €3,500 monthly contribution and current portfolio drift:

| Instrument | Ticker | Target | Current | Drift | This Month | Amount |
|-----------|--------|--------|---------|-------|------------|--------|
| iShares Core MSCI EM IMI | IS3N | 13.75% | 10.20% | -3.55% | 28.4% | €994 |
| iShares Core S&P 500 | SXR8 | 19.25% | 17.10% | -2.15% | 17.2% | €602 |
| ... | ... | ... | ... | ... | ... | ... |
| VanEck Semiconductor ETF | SMH | 15.00% | 18.30% | +3.30% | 0.0% | €0 |

**Total allocated:** €3,500
**Unallocated:** €0

[If not fully rebalanced:]
> At current contribution levels, the portfolio is estimated to reach target weights in approximately [N] months.

[If sell suggestions:]
### Sell Recommendations

The following positions are significantly overweight and cannot be corrected through contributions alone within 12 months:

| Instrument | Current Drift | Sell Amount | Tax Impact* |
|-----------|--------------|-------------|-------------|
| [Position] | +X.X% | €X,XXX | ~€XXX |

*Estimated tax on realized gains at 26.375% (Germany). Actual tax depends on your cost basis.
```

### Macro Landscape — Update Focus

If themes were refreshed, show the full updated themes. If themes are unchanged, keep it brief:

```markdown
## 3. Macro Landscape

*Research date: YYYY-MM-DD [N days ago]*

**Theme status:**
- AI Infrastructure Boom: ✓ Thesis intact. [One-line update if available.]
- European Rearmament: ✓ Thesis intact.
- [Theme X]: ⚠ Thesis weakened — [brief explanation].

[Only include full theme writeups if themes were refreshed or materially changed.]
```

### Risk Factors — Update

Keep existing risk factors that are still relevant. Add new ones if:
- A hypothesis was weakened but not removed
- Drift has created new concentration risks
- Market conditions have introduced new risks since last review

Remove risk factors that are no longer relevant (e.g., a risk that has been addressed by the rebalancing actions).

---

## Updating portfolio.json After Maintenance

After the maintenance cycle completes, `portfolio.json` should be updated with:

```json
{
  "updated": "YYYY-MM-DD",
  "positions": [
    {
      "...existing fields...",
      "current_weight_pct": 22.1,
      "target_weight_pct": 19.25
    }
  ]
}
```

**Fields to update:**
- `updated` → today's date
- `current_weight_pct` for each position → from user-provided data
- `target_weight_pct` → only if targets were modified during review
- `hypothesis` → only if thesis was revised
- `analysis` section → only if target weights changed (re-run scripts)

**Fields NOT to modify:**
- `instrument` data — this comes from the security screener (Stage 4). Don't change it during maintenance unless the user explicitly requests re-screening.
- `created` date
- `version`
- `watchlist` — unless the user requests changes

---

## When to Invoke Other Skills or Agents

During maintenance, you may need to hand off to other pipeline components:

| Situation | Action |
|-----------|--------|
| Macro themes are stale (>30 days) and user agrees to refresh | Read `references/3-macro-research.md` and follow its instructions |
| A thesis is invalidated and user wants to find a replacement instrument | Invoke the `security-screener` agent with a screening brief |
| Target weights changed significantly (user adjusts allocation) | Read `references/5-portfolio-construction.md` for the weight adjustment workflow, or handle inline if changes are minor |
| User wants a full report regeneration (not just maintenance updates) | Read `references/6-report-generation.md` and follow its instructions |
| User wants to change their risk profile or contribution amount | Read `references/1-investor-profile.md` for Stage 1 re-entry |

For minor adjustments (tweaking one weight, updating a hypothesis), handle them directly within the maintenance flow rather than routing to another stage. Use your judgment on complexity — if the change is a one-line weight adjustment, do it here. If it's a full portfolio restructuring, route to the appropriate stage.
