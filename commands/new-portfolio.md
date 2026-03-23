# /new-portfolio

Start a new portfolio build using the CoFolio pipeline.

## What to do

### Step 1 — Check for existing pipeline files

Look in the current working directory for any of these files:

- `investor-profile.md`
- `asset-allocation.md`
- `macro-themes.md`
- `portfolio.json`
- `report.md`

### Step 2 — Branch on what you find

**If none of those files exist:**

Tell the user: "Starting a new portfolio from scratch." Then invoke the `orchestrator` skill, which will route to Stage 1 (Investor Profile).

**If one or more of those files exist:**

List the files found and tell the user they already have an in-progress or completed portfolio in this directory. Ask them to choose:

> I found an existing portfolio in this directory:
> - [list found files]
>
> What would you like to do?
> 1. **Resume** — continue from where you left off (Stage N: [current stage name])
> 2. **Archive and start fresh** — move existing files to `archive/YYYY-MM-DD/` and begin a new portfolio
>
> Reply with **1** or **resume** to continue, or **2** or **archive** to start fresh.

Wait for their response before proceeding.

- If they choose **resume**: invoke the `orchestrator` skill. It will detect the current stage and continue from there.
- If they choose **archive**: create a subdirectory named `archive/` + today's date in `YYYY-MM-DD` format (e.g., `archive/2026-03-24/`). Move all found pipeline files into it. Then tell the user the files have been archived, and invoke the `orchestrator` skill to start Stage 1 fresh.

### Step 3 — Hand off to the orchestrator

In all paths, the final action is invoking the `orchestrator` skill. It will handle routing, state detection, and calling the correct stage skill.
