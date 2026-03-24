# Macro Research — Reference Material

This file contains the research quality checklist, investability assessment framework, confidence calibration guide, and the output template for `macro-themes.md`. Read this when you need to evaluate agent research quality, shape themes, or format the final output.

---

## Research Quality Checklist

Use this checklist to evaluate the macro researcher agent's output before presenting it to the user. The agent should have covered all six categories — if any are missing, note the gap.

### Category Coverage

| # | Category | What to look for | Red flag if missing |
|---|----------|------------------|---------------------|
| 1 | Monetary Policy & Rates | Rate direction for Fed, ECB, BoJ, PBoC; QT/QE status; yield curve; real rates vs. inflation | Always relevant — rates affect every asset class |
| 2 | Geopolitics & Trade | Active conflicts, sanctions, trade policy shifts, upcoming elections, regulatory changes | Geopolitical risk is often underpriced; missing it is a blind spot |
| 3 | Technology & Innovation | AI/ML spending, semiconductor cycles, energy transition tech, biotech, digitization | Tech themes are frequently the highest-conviction among retail investors |
| 4 | Commodities & Energy | Oil/gas supply-demand, industrial metals, precious metals, energy transition materials | Commodities drive inflation expectations and sector rotation |
| 5 | Sector Rotations | Leading vs. lagging sectors, value/growth dynamics, cyclicals vs. defensives, earnings revisions | Tells you where the market cycle is and where momentum sits |
| 6 | Regional Dynamics | US, Europe, China, EM, Japan — economic health, policy direction, relative valuations | Geographic allocation is a major portfolio decision |

### Thesis Quality

A good theme thesis should be:

- **Specific:** "AI inference demand is shifting semiconductor capex from leading-edge logic to advanced packaging and HBM memory" — not "tech is growing"
- **Causal:** Explains the mechanism — why this is happening and why it affects markets
- **Data-grounded:** Cites specific numbers, dates, or sources where possible
- **Forward-looking:** Describes what's likely to happen, not just what already happened
- **Investable:** There are liquid instruments (ETFs, stocks, bonds) that can express this theme

### Completeness per Theme

Each theme should have all of these fields filled in. If any are missing or vague after the agent's research, improve them before presenting to the user:

- [ ] Clear, descriptive theme name
- [ ] Category assignment (one of the six categories)
- [ ] Thesis (2-4 sentences, specific and causal)
- [ ] Time horizon (structural / cyclical / tactical — with duration)
- [ ] Relevant sectors (specific, not just "various")
- [ ] Relevant regions (specific, not "global" unless truly global)
- [ ] Key risks (what could go wrong)
- [ ] Invalidation triggers (specific, observable, falsifiable)
- [ ] Confidence rating (High / Medium / Speculative)

---

## Investability Assessment Framework

Before presenting a theme to the user, assess whether it's actually investable. A fascinating macro insight that can't be expressed in a portfolio is interesting reading but not useful for this pipeline.

### Investability Criteria

| Criterion | Question | Pass | Fail |
|-----------|----------|------|------|
| Instrument availability | Are there liquid ETFs, stocks, or bonds that express this theme? | At least 2-3 instruments exist on major exchanges | No clear instruments, or only illiquid / niche products |
| Differentiation | Does this theme justify a portfolio tilt vs. broad market exposure? | Theme targets a specific sector, region, or factor that broad indices don't adequately capture | Theme is effectively "own the market" — already well-captured by a broad index fund |
| Time horizon fit | Is the theme's horizon compatible with a portfolio review cycle? | 6 months to multi-year — actionable within a typical rebalancing cadence | Too short (days/weeks — more trading than investing) or too long with no near-term catalyst |
| Falsifiability | Can the thesis be invalidated by observable data? | Clear triggers: spending data, earnings, policy decisions, economic indicators | Unfalsifiable narrative or moving goalposts |

### How to Handle Non-Investable Themes

If the agent produces a theme that fails investability but is genuinely interesting:

- **Mention it briefly** in the presentation as "notable macro development" rather than an investable theme
- **Don't include it** in the structured theme list that the user selects from
- If the user specifically asks about it, explain why it's hard to express in a portfolio and suggest the closest proxy if one exists

---

## Confidence Calibration Guide

The agent assigns confidence ratings, but they sometimes need recalibration. Use these benchmarks:

### High Confidence

All of these should be true:

- Supported by multiple independent, credible data sources
- Clear causal mechanism linking the thesis to market outcomes
- Institutional consensus is forming (sell-side research, central bank communications, major publications converging)
- Observable in current market data (price action, flows, earnings trends align with the thesis)

**Example:** "Central banks are cutting rates" when the Fed, ECB, and BoE have all begun easing cycles with forward guidance suggesting continuation.

### Medium Confidence

Most of these are true:

- Supported by credible analysis but actively debated
- Causal mechanism is plausible but has untested assumptions
- Some contradictory signals exist (e.g., strong employment data vs. manufacturing recession)
- Timing is uncertain even if direction is clear

**Example:** "China stimulus will drive an EM recovery" when stimulus has been announced but scale and transmission to markets is unclear.

### Speculative

One or more of these:

- Based on emerging signals without strong current evidence
- Contrarian thesis — goes against prevailing market consensus
- Forward-looking inference that requires multiple assumptions to hold
- Limited data availability (new technology, new geopolitical dynamic)

**Example:** "Nuclear renaissance driven by AI datacenter power demand" when early contracts are signed but build-out timelines are 5-10 years and regulatory hurdles remain.

### When to Recalibrate

- Agent says "High" but the thesis relies on a single data point or source → downgrade to Medium
- Agent says "Speculative" but the thesis is well-supported by multiple converging data sources → upgrade to Medium or High
- Agent hedges extensively within a "High confidence" theme → the hedging suggests it's actually Medium

---

## Profile-Aware Presentation Guide

When an investor profile exists, use it to contextualize — not filter — the themes.

### Alignment Signals

| Profile Trait | Theme Alignment | How to Note It |
|--------------|-----------------|----------------|
| Aggressive risk + long horizon | Structural technology/growth themes | "Aligns with your long-horizon growth orientation" |
| Conservative risk + income focus | Defensive sectors, rate-sensitive themes | "Relevant to your income-oriented approach" |
| ESG/ethical exclusions | Themes involving excluded sectors | "Note: this theme involves [excluded sector] — flagging for awareness, though you may choose to express it through adjacent instruments" |
| Geographic focus (e.g., Europe-based) | Regional themes for their home market | "Particularly relevant given your European base and XETRA access" |
| Stated convictions (e.g., "I believe in AI") | Themes that match stated beliefs | "This connects to the AI conviction you mentioned in your profile" |

### What NOT to Do

- Don't hide themes that don't match the profile — the user should see the full landscape
- Don't rank themes by profile fit — present them by category, neutrally
- Don't say "this theme is perfect for you" — say "this aligns with [specific profile trait]"

---

## Output Template

Use this exact structure for `macro-themes.md`. Every theme the agent found goes in the file — selected or not.

```markdown
# Macro Themes & Market Research

*Researched: [YYYY-MM-DD]*

## Theme: [Descriptive Theme Name]

- **Category:** [Monetary Policy | Geopolitics | Technology | Commodities | Sector Rotation | Regional]
- **Thesis:** [2-4 sentences: what is happening, why it matters for markets, and the investment implication]
- **Time horizon:** [Structural (multi-year) | Cyclical (6-18 months) | Tactical (1-6 months)]
- **Relevant sectors:** [comma-separated list of specific sectors]
- **Relevant regions:** [comma-separated list of specific regions]
- **Key risks:** [what could go wrong or limit the opportunity]
- **Invalidation triggers:** [specific, observable conditions that would kill the thesis]
- **Confidence:** [High | Medium | Speculative]
- **Selected by user:** [Yes | No]

<!-- Repeat for each theme -->

## User-Added Themes

<!-- If the user adds custom themes, use the same structure above but note: -->
<!-- - **Source:** User conviction (not from macro research agent) -->
<!-- If no user-added themes: -->
*None at this time.*
```

### Template Notes

- **Date format:** Use ISO 8601 (YYYY-MM-DD)
- **One theme per `##` heading:** Don't nest themes or combine them
- **All fields required:** Every theme must have every field filled in. No "N/A" or "Various" — be specific
- **User-added themes:** Use the same field structure but add a `**Source:** User conviction` field so downstream stages know this wasn't from the research agent
- **Ordering:** Group by category. Within each category, order by confidence (High → Medium → Speculative)
