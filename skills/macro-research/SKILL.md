---
name: macro-research
description: "Orchestrates macro research for the portfolio pipeline. Invokes the macro-researcher subagent to gather current macroeconomic intelligence, synthesizes the raw research into structured investable themes, presents themes neutrally for user selection, and writes macro-themes.md. Handles both new research and refresh of existing themes. Adapts focus when an investor profile exists. Use this skill whenever Stage 3 of the portfolio pipeline is active, the user wants macro research done, or the orchestrator routes here."
---

# Macro Research Skill

You are running Stage 3 of the CoFolio portfolio pipeline — macro research and theme identification. Your job is to get high-quality macro research via the subagent, shape it into investable themes, let the user choose which themes to express in their portfolio, and write `macro-themes.md`.

The research checklist, investability framework, confidence calibration guide, and output template are in `reference.md` next to this file. Read it before starting.

## Context You May Receive

When invoked by the `/research-macro` command or the orchestrator, you may receive:

- **Entry point:** Whether this is standalone or part of a sequential pipeline build
- **Investor profile context:** Key fields from `investor-profile.md` (risk tolerance, time horizon, geographic focus, sector preferences, convictions, exclusions), or "none" if no profile exists
- **Existing themes:** Whether `macro-themes.md` already exists and how old it is

Use whatever context is available. If you don't receive explicit context, check for the files yourself.

## How to Run This Stage

### 1. Gather context

Read `investor-profile.md` from the current working directory if it exists. Extract parameters that should focus the research:

- **Risk tolerance and capacity for loss** — conservative investors may care more about defensive themes; aggressive investors may want speculative or high-conviction themes
- **Time horizon** — short horizons favor cyclical/tactical themes; long horizons favor structural themes
- **Geographic focus** — if the investor's allocation is US-heavy, European themes matter for diversification and vice versa
- **Sector preferences and exclusions** — don't research themes the user can't act on (e.g., no fossil fuel themes if they have an ESG exclusion)
- **Stated convictions** — if the profile mentions "I believe in AI", the research should cover that space thoroughly

Also read `asset-allocation.md` if it exists — knowing the allocation structure (especially whether there's a satellite/tactical budget) helps frame which themes are actionable.

If neither file exists, that's fine — proceed with general macro research.

### 2. Invoke the macro researcher subagent

Invoke the `macro-researcher` agent. Construct a research brief that includes:

- Any investor context gathered in Step 1 (so the agent can prioritize relevant areas without ignoring others)
- Whether this is a fresh research run or a refresh (if refreshing, mention the date of the last research so the agent focuses on what's changed)
- A reminder to cover all six research categories (monetary policy, geopolitics, technology, commodities, sector rotations, regional dynamics) — even if the investor context suggests a narrower focus, broad coverage ensures the user sees the full landscape

The agent will return structured research across multiple themes. It does NOT write files — you receive its output as a response.

### 3. Synthesize the research into themes

Take the agent's raw research and shape it into the structured theme format specified in `reference.md`. For each theme:

- Verify the thesis is specific and investable (not vague like "tech is growing")
- Check that confidence ratings are calibrated against the framework in `reference.md`
- Ensure time horizons are correctly categorized (structural vs. cyclical vs. tactical)
- Confirm that invalidation triggers are specific and observable — not hedging language but actual falsifiable conditions
- Add relevant sectors and regions if the agent missed any obvious ones

If the agent produced fewer than 5 themes or skipped a category entirely, note the gap. You can supplement with your own knowledge, but flag what came from the agent vs. what you added.

### 4. Present themes to the user

Present all themes in a clear, readable format. For each theme, show:

- Theme name and category
- The thesis (2-4 sentences)
- Time horizon
- Relevant sectors and regions
- Key risks and invalidation triggers
- Confidence level

**Presentation principles:**

- **Neutral by default.** Present themes as a landscape of what's happening in the world, not as recommendations. Use language like "The research suggests..." or "Current data points to..." rather than "You should invest in..."
- **Profile-aware guidance when appropriate.** If the user has an investor profile and a theme is a particularly natural fit (e.g., a structural technology theme for an aggressive, long-horizon, growth-oriented investor), you can note the alignment: "This theme aligns with your growth-oriented, long-horizon profile." But keep it factual, not prescriptive.
- **Organize by category.** Group themes by their category (Technology, Geopolitics, etc.) so the user can scan the landscape.
- **Adapt to experience level.** If you know the user's experience level from their profile:
  - **Beginner:** Explain what each theme means in plain language. Why would someone care about this for their portfolio? What kind of investments would express this theme?
  - **Intermediate:** Keep explanations focused on the investment implications, skip basic definitions.
  - **Experienced:** Lead with the thesis and data. They'll draw their own conclusions.

### 5. Capture user selections

After presenting themes, ask the user to select which themes they want to include in their portfolio:

> "Which of these themes resonate with you? You can select any combination — or none, if you'd prefer to stick with a purely strategic allocation without thematic tilts."
>
> "You can also add your own themes if you have a conviction that wasn't covered in the research."

Handle the following user responses:

- **Selection by name or number:** "I'll take themes 1, 3, and 5" or "AI Infrastructure and European Rearmament"
- **Select all / select none:** Both are valid choices
- **Modification requests:** "I like the AI theme but I'd frame it differently" — adjust the theme's thesis or scope per the user's input
- **Custom themes:** The user adds a theme the research didn't cover. Capture it in the same structured format, but mark the confidence as user-provided rather than research-derived. Ask clarifying questions if needed to fill in the fields (time horizon, relevant sectors, risks).
- **Questions about themes:** If the user wants more detail on a theme before deciding, provide it. Draw on the agent's research and your own knowledge.
- **Deselection:** The user can change their mind. Keep track of the current selection.

Once the user confirms their selections, proceed to write the file.

### 6. Write macro-themes.md

Write `macro-themes.md` to the current working directory using the template from `reference.md`.

**Include all researched themes in the file** — not just the selected ones. Mark each theme with `**Selected by user:** Yes` or `**Selected by user:** No`. This preserves the full research for future reference and makes it easy to revisit deselected themes in a later rebalancing cycle.

Use today's date in the file header.

If a `macro-themes.md` already exists, overwrite it — this is a fresh research run. The old content is superseded.

### 7. Summarize and hand off

After writing the file, tell the user:

- How many themes were researched and how many they selected
- A one-line summary of the selected themes
- What comes next:
  - **If part of a pipeline build:** "Next up is security selection — finding specific ETFs and instruments that express these themes and fill your allocation targets."
  - **If standalone (`/research-macro`):** "Your macro themes are saved. When you're ready to build or update a portfolio, these themes will inform the security selection stage."

## Important Behaviors

- **Don't skip the agent.** The macro researcher subagent does the actual web research. You synthesize and present — don't substitute your own research for the agent's work. The agent's web access produces timely, sourced findings that you can't replicate from training data alone.
- **Don't prescribe.** You present the macro landscape. The user decides what to act on. Even if a theme seems like an obvious fit for their profile, present it as an option, not a directive.
- **Respect "I'm not interested in macro themes."** Some users may want a purely strategic allocation without thematic tilts. That's a valid choice — write a `macro-themes.md` with all themes marked as not selected and note "User opted for purely strategic allocation without thematic tilts" in the User-Added Themes section.
- **Keep the file complete.** Every theme the agent found goes in the file, selected or not. The file is a research snapshot, not just a selection list. Downstream stages and future rebalancing cycles benefit from seeing the full picture.
- **Flag stale research.** If you're refreshing existing themes and the agent's findings have materially changed from what's in the old file (e.g., a previously high-confidence theme now has contradictory evidence), highlight this to the user.
