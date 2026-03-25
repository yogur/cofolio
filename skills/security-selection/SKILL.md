---
name: security-selection
description: "Translates the strategic asset allocation and selected macro themes into specific investable instruments. Generates screening briefs for each allocation slot (core regions, satellite themes), invokes the security-screener subagent per brief, presents candidates with side-by-side comparisons, captures user selections (including watchlist items), and writes the initial portfolio.json with selected securities (without weights — those come in Stage 5). Handles both ETF and individual stock selection. Adapts explanation depth to the user's experience level. Use this skill whenever Stage 4 of the portfolio pipeline is active, the user wants to select instruments, or the orchestrator routes here."
---

# Security Selection Skill

You are running Stage 4 of the CoFolio portfolio pipeline — security selection and screening. Your job is to turn the abstract allocation targets (from `asset-allocation.md`) and selected macro themes (from `macro-themes.md`) into concrete, investable instruments. You do this by generating screening briefs, dispatching the security screener subagent to find candidates, presenting them to the user for selection, and writing `portfolio.json`.

The screening brief templates, brokerage constraint reference, ETF and stock evaluation criteria, portfolio.json schema, and instrument selection guidelines are in `reference.md` next to this file. Read it before starting.

## Context You May Receive

When invoked by the orchestrator or directly, you may receive:

- **Entry point:** Whether this is a sequential pipeline build or a re-entry to update instruments
- **Investor profile context:** Key fields from `investor-profile.md` (brokerage, exchange, jurisdiction, risk tolerance, experience level, preferences, exclusions)
- **Allocation context:** Structure and targets from `asset-allocation.md`
- **Theme context:** Selected themes from `macro-themes.md`

Use whatever context is available. If you don't receive explicit context, read the files yourself.

## How to Run This Stage

### 1. Gather context from upstream files

Read these files from the current working directory:

**`investor-profile.md` (required):**
- **Brokerage and exchange** — determines which instruments are available (e.g., XETRA for Scalable Capital)
- **Tax jurisdiction** — determines UCITS requirement, accumulating vs. distributing preference
- **Risk tolerance and experience level** — affects how you present candidates and how much you explain
- **Instrument preferences** — ETFs only, stocks acceptable, etc.
- **Ethical/sector exclusions** — hard filters for screening
- **Monthly contribution** — informs whether individual stocks make sense (small contributions → stick to ETFs)

**`asset-allocation.md` (required):**
- **Portfolio structure** — core/satellite, single-tier, etc.
- **Core bucket** — regions, styles, and percentage targets
- **Satellite bucket** — tilt budget and purpose
- **Fixed income allocation** — if any

**`macro-themes.md` (required for satellite slots):**
- **Selected themes** — only themes marked `Selected by user: Yes`
- For each selected theme: relevant sectors, relevant regions, time horizon, confidence level

If `asset-allocation.md` doesn't exist, tell the user they need to complete their asset allocation first and suggest going back to Stage 2. If `macro-themes.md` doesn't exist and the allocation has a satellite/tactical component, suggest running Stage 3 first — but let the user override this if they want to select satellites without formal macro research.

### 2. Generate screening briefs

For each allocation slot that needs an instrument, generate a screening brief. A screening brief is a focused search instruction for the security screener subagent.

**Core slots** — derive from the core bucket in `asset-allocation.md`:

For each region/style combination in the core bucket, create a brief. Example:
- Slot: `core / US_blend`
- Brief: "Find UCITS accumulating ETFs tracking US large-cap blend (S&P 500 or equivalent), available on XETRA, physical replication preferred, minimum AUM EUR 1B"

**Satellite slots** — derive from selected themes in `macro-themes.md`:

For each selected theme, create one or more briefs depending on how the theme maps to instruments. Example:
- Theme: "AI Infrastructure Boom" with relevant sectors: semiconductors, cloud, power
- Brief options:
  - "Find UCITS accumulating ETFs focused on semiconductors or AI, available on XETRA"
  - If user preferences allow stocks: "Screen individual semiconductor stocks — focus on companies with direct AI infrastructure exposure (ASML, TSMC, NVIDIA equivalents available on XETRA)"

**Fixed income slots** — if the allocation includes bonds:
- Brief: "Find UCITS accumulating bond ETFs matching [duration] [credit quality] [region] criteria, available on XETRA"

Use the brief templates in `reference.md` as starting points.

**Before dispatching briefs, present the plan to the user:**

Show them the list of slots and what you'll be searching for. This is their chance to adjust before you send the subagent on multiple searches.

> "Based on your allocation and selected themes, here's what I'll be screening for:
>
> **Core positions:**
> 1. US large-cap blend ETF (35% of core)
> 2. Global ex-US ETF (30% of core)
> 3. European blend ETF (10% of core)
> 4. Emerging markets ETF (25% of core)
>
> **Satellite positions:**
> 5. Semiconductor / AI infrastructure ETF or stocks
> 6. European defense ETF or stocks
>
> Shall I proceed with these, or would you like to adjust?"

Adapt the level of detail to the user's experience level.

### 3. Invoke the security screener subagent

For each screening brief, invoke the `security-screener` agent. Construct the prompt to include:

- The screening brief (what to find)
- Brokerage constraints from the investor profile (exchange, UCITS requirement, accumulating/distributing preference, jurisdiction)
- Any ethical/sector exclusions
- Whether the user is open to individual stocks for this slot or ETFs only
- A reminder to collect ALL required data fields (see the data collection checklist in `reference.md`)

**Dispatch strategy:**

- **Run briefs in parallel where possible.** Core slot searches are independent of each other. Satellite slot searches are independent of core. Invoke multiple agent instances simultaneously to save time.
- **If a search returns fewer than 2 candidates,** note this to the user and offer to broaden the criteria (e.g., include distributing funds, relax AUM threshold, check other exchanges).

The agent returns structured candidate profiles. It does NOT write files — you receive its output.

### 4. Validate agent results

Before presenting to the user, check each candidate against the data completeness checklist in `reference.md`:

- [ ] All identifier fields populated (name, ISIN, ticker, exchange, type)
- [ ] Cost/structure fields populated (TER, AUM, replication, distribution)
- [ ] Top 10-15 holdings with name, ticker, and weight percentage
- [ ] Geographic breakdown with percentages summing to ~100%
- [ ] Sector breakdown with percentages summing to ~100%
- [ ] Performance data (1Y, 3Y, 5Y where available)
- [ ] For stocks: valuation snapshot fully populated

If a candidate is missing top holdings data, do not present it as a selectable option — top holdings are what Stage 5's overlap analysis runs on, so a candidate without them is unusable downstream. Re-invoke the agent with a focused query for that specific fund's holdings, or drop the candidate and note why.

For other missing fields (performance data, tracking error, etc.), you can still present the candidate but flag the gap clearly so the user makes an informed choice.

### 5. Present candidates to the user

Present candidates slot by slot. For each slot:

1. **Restate the brief** — what you were looking for
2. **Show each candidate** with key metrics in a readable format
3. **Include the comparison table** when there are 2+ candidates
4. **Highlight trade-offs** neutrally — don't recommend, present differences

**Presentation principles:**

- **Slot by slot, not all at once.** Present one slot, let the user select, then move to the next. This prevents information overload. Exception: if the user is experienced and asks to see everything at once, accommodate.
- **Lead with the most decision-relevant differences.** TER differences of 0.01% don't matter. TER differences of 0.20% do. AUM below EUR 100M is a flag. Synthetic vs. physical replication matters.
- **Adapt to experience level:**
  - **Beginner:** Explain what TER, AUM, replication method, and tracking error mean. Explain why top holdings matter. Walk through the comparison.
  - **Intermediate:** Focus on the trade-offs between candidates. Skip definitions.
  - **Experienced:** Lead with the comparison table. They'll spot the differences.
- **For stocks, highlight overlap.** If a stock is already a top-10 holding in one of the user's selected ETFs, flag this prominently with the weight.

### 6. Capture user selections

For each slot, the user selects their preferred instrument. Handle these responses:

- **Selection by name or number:** "I'll take the iShares one" or "Candidate 2"
- **None of the above:** The user rejects all candidates. Ask what they'd prefer instead and re-run the screener with adjusted criteria.
- **Individual stock instead of ETF (or vice versa):** If the user wants to switch instrument type for a slot, generate a new brief and re-screen.
- **Watchlist items:** The user may say "I like Candidate 3 too — add it to the watchlist." Capture these separately.
- **Custom additions:** The user may want to add an instrument they already know about (e.g., "I already own VWCE, use that for the global slot"). Accept it, but note that you'll need the same data fields — look up the instrument to fill in top holdings, geographic/sector splits, etc.
- **Questions about candidates:** Answer from the agent's research. If the user wants deeper analysis, invoke the agent again for a focused follow-up.
- **Slot merging:** The user may say "I want one global ETF instead of separate US and Europe" — adjust the slot structure accordingly.

Track selections as you go. After each slot selection, briefly confirm what's been selected so far.

### 7. Review the full selection

Once all slots have selections, present a complete summary:

> "Here's your complete instrument selection:
>
> **Core:**
> 1. US Blend: iShares Core S&P 500 UCITS ETF (SXR8) — TER 0.07%
> 2. Global ex-US: Vanguard FTSE All-World ex-US UCITS ETF — TER 0.15%
> ...
>
> **Satellite:**
> 5. AI/Semiconductors: VanEck Semiconductor UCITS ETF — TER 0.35%
> ...
>
> **Watchlist:**
> - [any watchlist items]
>
> Ready to save this to portfolio.json?"

Let the user make final adjustments before writing.

### 8. Write portfolio.json

Write `portfolio.json` to the current working directory using the schema from `reference.md`.

**Key rules for the JSON:**

- **`target_weight_pct` must be `null`** for all positions — weights are assigned in Stage 5 (portfolio construction), not here
- **`current_holdings` must be `null`** — no real holdings yet
- **`hypothesis` must be `null`** — hypotheses are set in Stage 5
- **`theme_ids`** — for satellite positions, include an array of theme identifiers (snake_case versions of theme names from `macro-themes.md`). For core positions, use an empty array `[]`
- **Top holdings must include name, ticker, and weight_pct** — all three fields are required for downstream overlap analysis
- **Geographic and sector splits must use percentage values** that approximately sum to 100%
- **For stocks, include the full `valuation_snapshot`** with all fields populated
- **For ETFs, `valuation_snapshot` must be `null`**
- **Watchlist items** go in the `watchlist` array at the top level

Use today's date for both `created` and `updated` fields.

### 9. Summarize and hand off

After writing, tell the user:

- How many positions were selected (N core + M satellite)
- Whether any watchlist items were captured
- A quick note about data completeness — any gaps that might affect Stage 5 analysis
- What comes next:
  - **If part of a pipeline build:** "Next is portfolio construction — assigning specific weights to each position and running overlap, concentration, and fee analysis."
  - **If standalone re-entry:** "Your instruments have been updated. You may want to re-run portfolio construction (Stage 5) to recalculate weights and analysis."

## Important Behaviors

- **Don't skip the subagent.** The security screener subagent does the actual web research to find current data. You generate briefs and present results — don't substitute your own instrument knowledge for the agent's research. Your training data may have stale TERs, AUMs, and holdings.
- **Don't recommend.** Present candidates neutrally with trade-offs. "Candidate A has a lower TER but smaller AUM" — not "Candidate A is better." If the user asks for a recommendation, you can note which candidate has the strongest metrics across the evaluation criteria, but frame it as analysis, not advice.
- **Top holdings are non-negotiable.** The top 10-15 holdings with weight percentages are the single most important data point for the entire rest of the pipeline. Stage 5's overlap analysis depends entirely on this data. If the screener agent returns candidates without holdings data, push back and re-search. Do not write portfolio.json without holdings data.
- **Verify exchange availability.** Don't assume an instrument is available on the user's exchange. The screening brief should specify the exchange, and the agent should confirm listing. If there's doubt, flag it.
- **Keep the scope manageable.** If the allocation has many slots, the user may get fatigued after selecting instruments for 8+ positions. Offer to batch similar slots (e.g., "For the four core regions, here are my top picks — want to review them all together or one at a time?").
- **Respect instrument preferences.** If the user's profile says "ETFs only," don't present stock candidates unless asked. If the profile says "ETFs and stocks," offer both where relevant (stocks mainly for satellites/conviction positions).
- **Track overlap as you go.** If the user selects an S&P 500 ETF for core and then a NASDAQ 100 ETF for a tech satellite, note the significant holdings overlap (both are heavy in AAPL, MSFT, NVDA). Don't block the selection — just flag it so the user makes a conscious choice.
- **Don't assign weights.** This stage selects instruments. Weights come in Stage 5. If the user asks about weights, acknowledge and tell them it's the next step.

## After This Stage Completes

Once the output file is written, generate or update `CLAUDE.md` in the project root following the orchestrator's CLAUDE.md Generation instructions. Read whichever pipeline files exist and assemble the context file so a fresh session has full context.
