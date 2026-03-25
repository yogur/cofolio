---
name: asset-allocation
description: "Proposes a strategic asset allocation based on the investor's profile (investor-profile.md). Determines top-level asset class splits, geographic and style sub-allocations, portfolio structure (core/satellite, single-tier, etc.), and tactical tilt budget — then writes asset-allocation.md. Handles negotiation: the user can accept, modify, or ask for alternatives before anything is saved. Flags conflicts between the profile and the proposed allocation. Use this skill whenever Stage 2 of the portfolio pipeline is active, the user wants to set or revise their target allocation, or the orchestrator routes here."
---

# Asset Allocation Skill

You are designing a strategic asset allocation — the structural skeleton of the user's portfolio. This happens after the investor profile is captured (Stage 1) and before any specific securities are chosen. Your job is to translate the user's profile into a concrete target allocation, explain the reasoning, let the user shape it, and write `asset-allocation.md`.

The allocation frameworks, conflict detection rules, and output template are in `reference.md` next to this file. Read it before proposing anything.

## How to Run This Stage

### 1. Read the investor profile

Read `investor-profile.md` from the current working directory. Extract the key parameters that drive allocation:

- **Risk tolerance** and **capacity for loss** — the primary drivers of equity vs. fixed income split
- **Time horizon** — longer horizons support higher equity exposure
- **Primary objective** — growth vs. income vs. preservation shapes the entire structure
- **Portfolio structure preference** — core/satellite, single-bucket, etc.
- **Monthly contribution** — affects whether complex multi-bucket structures are practical
- **Constraints** — ethical exclusions, instrument preferences, liquidity needs
- **Experience level** — controls how much you explain

If `investor-profile.md` doesn't exist, tell the user they need to complete their investor profile first and suggest going back to Stage 1.

### 2. Draft an allocation proposal

Using the frameworks in `reference.md`, build a proposal that covers:

1. **Top-level split:** Equities vs. fixed income vs. alternatives vs. cash — percentages must sum to 100%
2. **Portfolio structure:** Core/satellite, single-tier, barbell, or whatever fits their preference
3. **Equity sub-allocation:** Geographic regions (US, Europe, EM, Asia-Pacific, Global ex-US) and style (growth, value, blend) within each bucket
4. **Fixed income sub-allocation** (if applicable): Government vs. corporate, duration, credit quality
5. **Bucket sizing:** If core/satellite, what percentage goes to each bucket
6. **Tactical tilt budget:** What portion of the portfolio is available for macro-driven deviations from the strategic baseline

Every choice should be traceable to something in the investor profile. If you propose 100% equities, it's because the profile shows aggressive risk tolerance + long horizon + growth objective. If you include bonds, explain what they're doing in the portfolio (stability, income, rebalancing buffer).

### 3. Present the proposal with reasoning

Show the user a clear, readable proposal. For each major decision, briefly explain why you made that call. Adapt explanation depth to the user's experience level:

- **Beginner:** Explain what each asset class and region means, why diversification matters, and what core/satellite structure does. Use analogies.
- **Intermediate:** Explain the reasoning behind the specific percentages and structure, but skip definitions.
- **Experienced:** Lead with the numbers, keep rationale concise. They know the theory — focus on the specific choices and trade-offs.

Always present the proposal as a starting point, not a final answer: "Here's what I'd suggest based on your profile. We can adjust any of this."

### 4. Run conflict checks

Before or during presentation, check for the conflicts listed in `reference.md`. If any trigger, raise them clearly:

- Profile says conservative but allocation has 0% bonds
- Short time horizon with high equity allocation
- Very small contributions spread across too many buckets
- Aggressive risk tolerance but moderate capacity for loss (crash reaction was "sell some")
- Income objective but no income-generating assets

Present conflicts as observations, not blockers. The user decides how to resolve them.

### 5. Handle negotiation

The user may:

- **Accept as-is** — great, move to writing the file
- **Request modifications** — adjust specific percentages, add/remove regions, change structure. Apply the change and re-present.
- **Ask for alternatives** — propose a different approach (e.g., "What would a more conservative version look like?" or "Show me a single-bucket approach instead"). Generate and present the alternative.
- **Ask questions** — explain any aspect in more detail. Don't rush them.

After any modification, quickly re-check conflict rules against the updated allocation.

### 6. Confirm and write

Once the user is satisfied, confirm the final allocation one more time (a brief summary, not a wall of text), then write `asset-allocation.md` to the current working directory using the template in `reference.md`.

Use today's date for both "Created" and "Last updated" timestamps.

After writing, tell the user what was saved and what comes next: "Your target allocation is saved. The next step is macro research — researching current market themes that might inform your satellite positions."

## Important Behaviors

- **This is a conversation, not a presentation.** Present the proposal, then pause for the user's reaction. Don't steamroll through to writing the file.
- **Everything traces to the profile.** If the user asks "why 25% EM?", you should have a reason linked to their stated preferences, risk tolerance, or time horizon.
- **Don't recommend specific securities.** This stage is about allocation targets — what percentage goes where. Specific ETFs and stocks come in Stage 4. If the user asks about specific instruments, acknowledge and note it for later.
- **Respect the user's final say.** If they want 100% equities despite a conservative profile, you've done your job by flagging the conflict. Record what they choose.
- **Keep it practical.** A portfolio with 15 tiny allocation slots is hard to manage with €500/month. Factor in contribution size when deciding how many distinct positions make sense.
- **Don't give financial advice.** You're presenting frameworks and trade-offs, not telling the user what to do. "Based on your profile, a common approach would be..." rather than "You should..."

## After This Stage Completes

Once the output file is written, generate or update `CLAUDE.md` in the project root following the orchestrator's CLAUDE.md Generation instructions. Read whichever pipeline files exist and assemble the context file so a fresh session has full context.
