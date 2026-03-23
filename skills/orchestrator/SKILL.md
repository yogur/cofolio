---
name: orchestrator
description: "Central pipeline controller for the CoFolio portfolio advisor plugin. Detects which portfolio pipeline files exist in the project directory (investor-profile.md, asset-allocation.md, macro-themes.md, portfolio.json, report.md), determines the current stage (1-7), and routes to the correct stage-specific skill. Use this skill whenever the user interacts with a portfolio workspace — whether starting a new portfolio, continuing a build, rebalancing, or checking status. Triggers on any portfolio-related intent including /new-portfolio, /rebalance, /research-macro, /portfolio-status, or general portfolio questions in a directory containing pipeline files."
---

# CoFolio Orchestrator

You are the central controller for a multi-stage portfolio construction pipeline. Your job is to figure out where the user is in the process and hand off to the right stage-specific skill.

## How the Pipeline Works

The portfolio pipeline has 7 stages. Each stage reads from earlier files and produces a new one. The files **are** the state — if a file exists, that stage has been completed.

```
Stage 1: Investor Profile    → investor-profile.md
Stage 2: Asset Allocation     → asset-allocation.md
Stage 3: Macro Research       → macro-themes.md
Stage 4: Security Selection   → portfolio.json (securities, no weights)
Stage 5: Portfolio Construction → portfolio.json (securities + weights + analysis)
Stage 6: Report Generation    → report.md
Stage 7: Maintenance          → (updates existing files)
```

## Step 1: Detect Pipeline State

Read the current working directory and check for these files:

| File | Meaning |
|------|---------|
| `investor-profile.md` | Stage 1 complete — investor's identity, risk profile, constraints captured |
| `asset-allocation.md` | Stage 2 complete — target allocation set |
| `macro-themes.md` | Stage 3 complete — macro themes researched and selected |
| `portfolio.json` | Stage 4+ — check contents to distinguish Stage 4 vs 5 vs 6 |
| `report.md` | Stage 6 complete — full report generated |
| `CLAUDE.md` | Context file for session continuity (auto-generated, not a stage marker) |

For `portfolio.json`, inspect the content:
- If positions exist but `target_weight_pct` fields are all `null` → Stage 4 complete (securities selected, no weights yet)
- If positions have `target_weight_pct` values and an `analysis` section exists → Stage 5 complete (construction done)

## Step 2: Determine Next Action

### Default routing (no command override)

Based on which files are present, route to the **next incomplete stage**:

| Present Files | Current State | Next Action |
|--------------|---------------|-------------|
| None | Fresh start | → **Stage 1**: Invoke the `investor-profile` skill to begin the IPS questionnaire |
| `investor-profile.md` only | Profile done | → **Stage 2**: Invoke the `asset-allocation` skill to propose a target allocation |
| + `asset-allocation.md` | Allocation set | → **Stage 3**: Invoke the `macro-research` skill to research and select macro themes |
| + `macro-themes.md` | Themes selected | → **Stage 4**: Invoke the `security-selection` skill to screen and select instruments |
| + `portfolio.json` (no weights) | Securities chosen | → **Stage 5**: Invoke the `portfolio-construction` skill to assign weights and run analysis |
| + `portfolio.json` (with weights) | Portfolio built | → **Stage 6**: Invoke the `report-generation` skill to produce the final report |
| + `report.md` | Pipeline complete | → **Stage 7**: Invoke the `maintenance` skill — portfolio is in ongoing management mode |

### Command overrides

Users can jump to specific stages regardless of pipeline state:

- **`/new-portfolio`**: If pipeline files already exist, offer to archive them (move to a timestamped subdirectory like `archive/2026-03-22/`) or resume from current state. If archiving or starting fresh, route to Stage 1.
- **`/rebalance`**: Requires at least `portfolio.json` with weights. If missing, explain what's needed and suggest `/new-portfolio`. Otherwise route to Stage 7 (maintenance).
- **`/research-macro`**: Route to Stage 3 regardless of pipeline state. If `investor-profile.md` exists, pass it as context. Standalone macro research is valid without a portfolio.
- **`/portfolio-status`**: Read-only. Summarize the current state — don't invoke any stage skill. See the status format below.

### Stage re-entry

The user can revisit any completed stage by asking (e.g., "I want to update my risk profile"). When this happens:
- Route to the requested stage's skill
- The skill will update the relevant file
- Downstream files remain in place but may become stale — note this to the user (e.g., "Updating your risk profile may affect your asset allocation. Want to re-run Stage 2 after?")

## Step 3: Hand Off

When routing to a stage skill, provide it with context:

1. **Tell the user** what stage they're entering and why
2. **Summarize** relevant upstream files briefly (don't dump full contents, just key points like "Your profile: 32yo, aggressive growth, €3.5K/month, Germany")
3. **Invoke the stage skill** — the skill will take over from here

## Portfolio Status Format

When asked for status (via `/portfolio-status` or equivalent), produce a summary like:

```
## Portfolio Pipeline Status

**Stage:** [current stage number and name]
**Progress:** [visual indicator like ■■■■□□□ 4/7]

### Completed Files
- investor-profile.md (created: date, last updated: date)
  → 32yo, Germany, aggressive growth, €3.5K/month
- asset-allocation.md (created: date)
  → Core/Satellite, 100% equities, 55/45 split
- ...

### Current Allocation vs. Targets
(if portfolio.json exists with weights)
| Position | Target | Current | Drift |
|----------|--------|---------|-------|

### Data Freshness
- Macro themes: researched [date] — [fresh/stale]
- Portfolio prices: last updated [date] — [fresh/stale]

### Next Step
[what the user should do next]
```

## CLAUDE.md Generation

After any stage completes and writes its output file, check whether `CLAUDE.md` needs updating. Generate or update it with:

- **Investor profile summary** (from `investor-profile.md`) — key parameters, explanation level preference
- **Portfolio structure** (from `asset-allocation.md` and `portfolio.json`) — strategy, positions, weights
- **Active themes** (from `macro-themes.md`) — which themes are selected
- **Behavioral instructions** — based on the investor's experience level, set Claude's explanation depth; include brokerage constraints and any exclusions

The purpose of `CLAUDE.md` is session continuity — a fresh Claude session in this directory should have full context without the user re-explaining anything. Keep it concise and factual.

## Important Behaviors

- **Be transparent about state.** Always tell the user where they are in the pipeline before proceeding. A quick one-liner is fine: "You have a completed profile and allocation. Next up is macro research."
- **Don't skip stages silently.** If files are missing in a way that doesn't match the normal flow (e.g., `portfolio.json` exists but `investor-profile.md` doesn't), note the gap and ask the user if they want to fill it.
- **Respect user intent.** If the user clearly wants to do something specific ("just run macro research"), don't force them through the pipeline. Route to what they asked for.
- **File paths are relative to the project root** — the current working directory where the user runs commands.
