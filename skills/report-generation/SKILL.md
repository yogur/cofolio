---
name: report-generation
description: "Produces a polished, human-readable report.md summarizing the entire portfolio — executive summary, investor profile recap, macro landscape, portfolio breakdown with per-position detail, analysis highlights (overlap, concentration, fee drag), a concrete action plan (what to buy/sell, monthly contribution strategy), risk factors, and watchlist. Reads all pipeline files (investor-profile.md, asset-allocation.md, macro-themes.md, portfolio.json) and synthesizes them into a single document. Use this skill whenever Stage 6 of the portfolio pipeline is active, the user wants to generate or regenerate the portfolio report, the orchestrator routes here after portfolio construction is complete, or the user asks for a report/summary of their portfolio."
---

# Report Generation Skill

You are running Stage 6 of the CoFolio portfolio pipeline — report generation. Your job is to read all upstream pipeline files and produce a comprehensive, actionable `report.md` that the user can reference as their portfolio's single source of truth.

The report template, section specifications, formatting standards, and example sections are in `reference.md` next to this file. Read it before writing the report.

## Context You May Receive

When invoked by the orchestrator or directly, you may receive:

- **Entry point:** Whether this is part of a sequential pipeline build (first report) or a re-generation (after weight adjustments, macro refresh, etc.)
- **Investor profile highlights:** Key fields from `investor-profile.md`
- **Portfolio summary:** Structure and position count from `portfolio.json`

Use whatever context is available. If you don't receive explicit context, read the files yourself.

## How to Run This Stage

### 1. Read all pipeline files

Read these files from the current working directory:

**`investor-profile.md` (required):**
- Demographics, risk profile, contributions, goals, constraints, preferences
- Experience level — controls the report's explanation depth
- Monthly contribution amount — needed for the action plan

**`asset-allocation.md` (required):**
- Portfolio structure (core/satellite, single-tier, etc.)
- Bucket targets and sub-allocations
- Strategy rationale

**`macro-themes.md` (required):**
- Selected themes with theses, time horizons, risks
- User-added themes
- Research date — note staleness if older than 30 days

**`portfolio.json` (required):**
- All positions with instruments, weights, and hypotheses
- The `analysis` section: weighted average TER, fee drag projections, top stock exposures, geographic split, sector split
- Watchlist items
- `data_as_of_date` fields — note these in the report for transparency

If any required file is missing, tell the user which file is missing and which pipeline stage produces it. Don't generate a partial report — the value is in the complete picture.

### 2. Synthesize the report

Write `report.md` following the template structure in `reference.md`. The report has 8 sections, each serving a specific purpose:

1. **Executive Summary** — Portfolio at a glance. The user should be able to read just this section and know what they own, why, and what to do next.

2. **Investor Profile Recap** — Key parameters from the IPS. Not a full copy — just the fields that shape the portfolio (risk tolerance, horizon, contributions, constraints).

3. **Macro Landscape** — Selected themes and how the portfolio is positioned for each. Connect themes to specific positions.

4. **Portfolio Breakdown** — The core of the report. Per-position detail grouped by bucket, with weights, instruments, fees, and hypotheses.

5. **Analysis Highlights** — Overlap findings, geographic and sector concentration, fee drag projection. Present the numbers with interpretation.

6. **Action Plan** — Concrete instructions: what to buy, in what order, how to allocate monthly contributions. This section makes the report actionable rather than just informational.

7. **Risk Factors** — Key risks to monitor and conditions that would trigger reassessment.

8. **Watchlist** — Instruments or themes being tracked but not yet actionable.

See `reference.md` for detailed guidance on each section's content and tone.

### 3. Calibrate tone and depth

The report should be:

- **Informative, not promotional.** Don't use sales language or hype. Present facts, reasoning, and trade-offs.
- **Balanced, not just bullish.** Every thesis has risks — include them. The report should help the user make clear-eyed decisions.
- **Practical, not theoretical.** The action plan should be specific enough that the user can open their brokerage and execute. "Buy X on XETRA" is better than "consider allocating to equities."
- **Concise but complete.** Don't pad sections with filler. If a section is naturally short (e.g., watchlist is empty), keep it short.

**Adapt depth to experience level** (from `investor-profile.md`):

- **Beginner:** Include brief explanations of concepts (TER, overlap, geographic diversification). Explain why each section matters.
- **Intermediate:** Focus on interpretation and implications. Skip basic definitions.
- **Experienced:** Lead with data and conclusions. Keep commentary minimal — they'll draw their own conclusions.

### 4. Present the draft to the user

Before writing `report.md`, present a brief overview of what the report will contain — not the full text, just the key highlights:

> "Here's what the report will cover:
> - **Portfolio:** N positions across core/satellite, 100% equities
> - **Key analysis:** Weighted TER of X%, top exposure NVDA at Y%, US-heavy at Z%
> - **Action plan:** Buy list for initial setup with €X/month contribution split
> - **Notable risks:** [1-2 key risks]
>
> I'll write the full report now. You can review and request changes after."

Then write the report. The user can request revisions after seeing the full output.

### 5. Write report.md

Write the complete report to `report.md` in the current working directory. Include the generation date in the header.

### 6. Offer revisions

After writing the report, ask the user if they want any changes:

- **Tone adjustments:** More/less technical, more/less detailed
- **Section additions:** Additional analysis, deeper dive on a specific theme
- **Action plan modifications:** Different contribution split, different execution order
- **Format preferences:** Different structure, emphasis on certain sections

Apply requested changes and rewrite `report.md`.

### 7. Summarize and hand off

After the report is finalized:

- Note that `report.md` is the user's reference document — they can share it, print it, or revisit it
- Mention that the portfolio is now in maintenance mode (Stage 7) — when they want to rebalance or update, they can use `/rebalance`
- If the orchestrator should update `CLAUDE.md`, note that

## Important Behaviors

- **Read reference.md before writing.** It contains the template, section specs, and formatting standards. Following it produces consistent, high-quality reports.
- **Use actual data, not placeholders.** Every number in the report comes from the pipeline files. Never invent or approximate — extract and compute from the source files.
- **Connect themes to positions.** The macro landscape section should clearly link each theme to the satellite positions that express it. Don't present themes and positions as disconnected lists.
- **The action plan must be executable.** Include instrument names, tickers, exchanges, and the exact weight-based allocation of contributions. The user should be able to follow it step by step.
- **Note data freshness.** Include `data_as_of_date` from `portfolio.json` instruments and the research date from `macro-themes.md`. If data is more than a week old, note it explicitly.
- **Don't re-run analysis scripts.** The analysis was already done in Stage 5 and is captured in `portfolio.json`'s `analysis` section. Use those numbers directly. If the analysis section is missing, suggest re-running Stage 5 first.
- **Fee drag projections should reference the investor's actual numbers.** Use their contribution amount and initial value, not generic assumptions. The numbers in the `analysis` section were already computed with these inputs by Stage 5.
- **Handle missing optional data gracefully.** If `watchlist` is empty, say so briefly. If `valuation_snapshot` is null for an instrument, skip valuation details for that position. Don't leave blank sections or placeholders.
