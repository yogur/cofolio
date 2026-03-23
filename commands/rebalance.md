---
name: rebalance
description: Review and rebalance an existing portfolio. Checks drift from targets, validates hypotheses, and produces updated recommendations.
---

# /rebalance

Trigger a rebalancing review for an existing portfolio. Requires `portfolio.json` to be present.

## What to do

### Step 1 — Check for `portfolio.json`

Look in the current working directory for `portfolio.json`.

**If `portfolio.json` does not exist:**

Tell the user clearly:

> No portfolio found in this directory — `portfolio.json` is missing.
>
> `/rebalance` requires a completed portfolio. Run `/new-portfolio` to build one from scratch.

Stop here. Do not invoke any skill or agent.

**If `portfolio.json` exists:**

Continue to Step 2.

### Step 2 — Inspect `portfolio.json` sub-state

Read `portfolio.json` to determine whether it is complete enough to rebalance:

- If positions exist but all `target_weight_pct` fields are `null` → portfolio construction (Stage 5) is not yet done. Tell the user:

  > Your portfolio has securities selected but weights have not been assigned yet.
  >
  > Run `/new-portfolio` and resume from Stage 5 (Portfolio Construction) to finish building your portfolio before rebalancing.

  Stop here.

- If positions have `target_weight_pct` values → proceed to Step 3.

### Step 3 — Check for other pipeline files (optional context)

Note which additional pipeline files are present for context passed to the orchestrator:

- `investor-profile.md`
- `asset-allocation.md`
- `macro-themes.md`
- `report.md`

These files make the rebalancing more informed but are not required.

### Step 4 — Confirm intent and hand off to orchestrator

Tell the user:

> Starting rebalancing review for your portfolio.
> [List any pipeline files found and note their approximate age if you can determine it.]

Then invoke the `orchestrator` skill with **maintenance intent** (Stage 7). The orchestrator will:

1. Detect that this is a rebalance request on an existing portfolio.
2. Identify which data may be stale (macro themes, current prices).
3. Collect only the missing or outdated information.
4. Run drift analysis and contribution optimization.
5. Produce updated recommendations and an updated report.
