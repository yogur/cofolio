# /research-macro

Standalone entry to Stage 3 (Macro Research). Research current macroeconomic conditions and geopolitical themes, regardless of where the portfolio pipeline currently stands.

## What to do

### Step 1 — Check for investor profile

Look in the current working directory for `investor-profile.md`.

- **If it exists:** Read it to extract key context — risk tolerance, investment horizon, geographic focus, sector preferences, and any stated convictions or exclusions. This will be used to focus the macro research on themes relevant to this investor's profile.
- **If it does not exist:** Proceed with general macro research. Do not ask the user to complete their investor profile first — this command is intentionally standalone.

### Step 2 — Check for existing macro themes

Look for `macro-themes.md` in the current working directory.

- **If it exists:** Note its date (from the file header) and tell the user:

  > Found existing macro themes researched on [date]. This run will refresh them.

- **If it does not exist:** This is a fresh research run. No need to mention it.

### Step 3 — Confirm and start

Tell the user what is about to happen:

- If investor profile was found:

  > Starting macro research tailored to your investor profile ([brief description of their profile, e.g., "growth-oriented, 20-year horizon, global equity focus"]).
  >
  > I'll research current macroeconomic conditions, geopolitical themes, and investable opportunities, then present them for your selection.

- If no investor profile:

  > Starting general macro research — no investor profile found in this directory.
  >
  > I'll research current macroeconomic conditions, geopolitical themes, and investable opportunities, then present them for your selection.
  >
  > Tip: Run `/new-portfolio` to build a full portfolio including an investor profile, which will focus the macro research on themes relevant to your situation.

### Step 4 — Invoke the macro research skill

Invoke the `macro-research` skill. Pass the following context:

- **Entry point:** standalone (`/research-macro` command, not part of a sequential pipeline build)
- **Investor profile context:** the key fields extracted in Step 1, or "none" if no profile exists
- **Existing themes:** whether `macro-themes.md` already exists and its age

The skill will:

1. Invoke the macro researcher subagent to research current conditions across all required categories (monetary policy, geopolitics, technology, commodities, sector rotations, regional dynamics).
2. Synthesize results into structured themes.
3. Present themes to the user for selection.
4. Write `macro-themes.md` (creating or overwriting it) with the user's selected themes.
