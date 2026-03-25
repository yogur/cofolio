---
name: maintenance
description: "Orchestrates the full portfolio maintenance and rebalancing flow for an existing portfolio. Detects stale data, collects current weights/prices from the user, runs drift analysis (scripts/drift.py) and contribution-based rebalancing optimization (scripts/rebalance.py), validates investment hypotheses against current conditions, optionally re-invokes macro-researcher or security-screener agents when themes or instruments need reassessment, re-runs portfolio analysis scripts (overlap, fees, concentration), and generates an updated maintenance report. Use this skill whenever Stage 7 of the portfolio pipeline is active, the user runs /rebalance, the orchestrator routes here for an existing portfolio, or the user wants to check drift, update weights, refresh macro themes, or review their portfolio after some time has passed."
---

# Maintenance Skill

You are running Stage 7 of the CoFolio portfolio pipeline — ongoing maintenance and rebalancing. Your job is to take an existing portfolio, figure out what data is stale or missing, collect only what's needed, run drift and rebalancing analysis, validate that the investment theses still make sense, and produce an actionable maintenance report.

The detailed reference material — script invocation, staleness criteria, hypothesis validation checklist, and maintenance report template — is in `reference.md` next to this file. Read it before starting.

## Context You May Receive

When invoked by the orchestrator or `/rebalance` command, you may receive:

- **Entry point:** Whether this is a `/rebalance` command, a direct request, or an orchestrator hand-off
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

See `reference.md` for output format and interpretation guidelines.

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

See `reference.md` for detailed presentation guidelines.

### 5. Validate investment hypotheses

This is what distinguishes maintenance from a simple rebalancing calculator. For each position, check whether the original investment thesis (the `hypothesis` field) still holds.

**For satellite/thematic positions — check theme validity:**

Read the invalidation triggers from `macro-themes.md` for each theme the position is linked to (via `theme_ids`). Ask:
- Has the thesis materially changed since the last research date?
- Have any invalidation triggers fired?
- Is there new information that strengthens or weakens the thesis?

If you have web access, briefly research the current state of each theme. If macro themes are stale (>30 days old), recommend a full macro refresh via the `macro-research` skill.

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

Produce an updated `report.md` focused on the maintenance context. The report should follow the same 8-section structure as the initial report (see `report-generation` skill) but with a maintenance focus:

- **Executive Summary:** Lead with what changed — drift status, key actions, any thesis updates
- **Action Plan:** This is the most important section for maintenance. Show the specific contribution allocation for this month, any sell orders if recommended, and the timeline to full rebalance
- **Macro Landscape:** Note any theme changes or staleness. If themes were refreshed, reflect the new research.
- **Risk Factors:** Update with any new risks identified during hypothesis validation

Invoke the `report-generation` skill to produce the report, or write it directly if the maintenance changes are minor and a full report regeneration isn't warranted. Use your judgment — if only drift and contribution allocation changed, a focused update is better than regenerating the entire report.

### 9. Summarize and close

After completing the maintenance cycle:

- Summarize the key actions: what to buy this month, any position changes, any items to monitor
- Note when the next maintenance review should happen (suggest monthly, or sooner if themes are stale or drift is significant)
- Remind the user they can run `/rebalance` anytime to trigger another maintenance cycle
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
