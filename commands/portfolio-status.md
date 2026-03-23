# /portfolio-status

Read-only command. Summarize the current state of the portfolio pipeline without invoking any stage skill or modifying any files.

## What to do

### Step 1 — Check for pipeline files

Look in the current working directory for these files and note their existence, creation dates, and last-updated dates (read the header line of each Markdown file, or the `updated` field in `portfolio.json`):

| File | Stage it represents |
|------|---------------------|
| `investor-profile.md` | Stage 1 — Investor Profile |
| `asset-allocation.md` | Stage 2 — Strategic Asset Allocation |
| `macro-themes.md` | Stage 3 — Macro Research |
| `portfolio.json` | Stage 4 or 5 — Security Selection / Construction |
| `report.md` | Stage 6 — Report Generation |

For `portfolio.json`, inspect its contents to determine sub-state:
- If positions exist but all `target_weight_pct` fields are `null` → Stage 4 complete (securities selected, no weights)
- If positions have `target_weight_pct` values and an `analysis` section exists → Stage 5 complete (portfolio constructed)

### Step 2 — Determine current stage

Use the same logic as the orchestrator:

| Files present | Current stage |
|--------------|---------------|
| None | No portfolio — Stage 0 |
| `investor-profile.md` | Stage 1 complete |
| + `asset-allocation.md` | Stage 2 complete |
| + `macro-themes.md` | Stage 3 complete |
| + `portfolio.json` (no weights) | Stage 4 complete |
| + `portfolio.json` (with weights + analysis) | Stage 5 complete |
| + `report.md` | Stage 6 complete → ongoing maintenance (Stage 7) |

### Step 3 — Produce the status summary

Print the following structured summary. Omit sections that have no data (e.g., skip "Current Allocation vs. Targets" if `portfolio.json` doesn't exist or has no weights).

```
## Portfolio Pipeline Status

**Stage:** [current stage number and name, e.g. "Stage 3 complete — Macro Research done"]
**Progress:** [filled/empty blocks, e.g. ■■■□□□□ 3/7]

### Completed Files
[For each file that exists, one bullet:]
- filename (created: YYYY-MM-DD, last updated: YYYY-MM-DD)
  → [one-line summary of key content]

### Current Allocation vs. Targets
[Only if portfolio.json exists with weights. Show a table:]
| Position | Instrument | Target % | Current % | Drift |
|----------|------------|----------|-----------|-------|
[If current_holdings is null for all positions, note: "Current prices not recorded — run /rebalance to update."]

### Data Freshness
[For each file that exists, note its age and whether it may be stale:]
- Investor profile: last updated [date] — [fresh / review recommended if > 6 months]
- Asset allocation: created [date] — [fresh / review recommended if > 12 months]
- Macro themes: researched [date] — [fresh if < 3 months / stale if 3-6 months / outdated if > 6 months]
- Portfolio: last updated [date] — [fresh / stale]
- Report: generated [date] — [fresh / stale]

### Next Step
[One sentence: what the user should do next, or "Portfolio is complete and in maintenance mode — run /rebalance to check for drift." if Stage 7.]
```

**If no files exist at all**, print:

```
No portfolio found in this directory.

Run /new-portfolio to start building your portfolio from scratch.
```

### Step 4 — Do not modify anything

This command is read-only. Do not write, edit, or create any files. Do not invoke any stage skill or subagent.
