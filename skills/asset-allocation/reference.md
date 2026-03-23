# Asset Allocation — Reference Material

This file contains allocation frameworks, conflict detection rules, practical sizing guidelines, and the output template for the asset allocation skill. Read this when you need to build a proposal, check for conflicts, or format the final `asset-allocation.md`.

---

## Allocation Frameworks

These are starting points, not rigid prescriptions. Combine them with the investor's specific profile to arrive at a proposal.

### Risk-Based Equity/Bond Split

The investor's risk tolerance and time horizon together determine the baseline equity/bond split. Use this table as a starting anchor, then adjust based on other profile factors.

| Risk Tolerance | Time Horizon < 5y | 5–10y | 10–20y | 20y+ |
|---------------|-------------------|-------|--------|------|
| Conservative | 20% eq / 60% FI / 20% cash | 30% eq / 55% FI / 15% cash | 40% eq / 50% FI / 10% cash | 45% eq / 45% FI / 10% cash |
| Moderate-Conservative | 30% eq / 50% FI / 20% cash | 45% eq / 45% FI / 10% cash | 55% eq / 40% FI / 5% cash | 60% eq / 35% FI / 5% cash |
| Moderate | 40% eq / 45% FI / 15% cash | 55% eq / 35% FI / 10% cash | 65% eq / 30% FI / 5% cash | 70% eq / 25% FI / 5% cash |
| Moderate-Aggressive | 50% eq / 35% FI / 15% cash | 65% eq / 30% FI / 5% cash | 80% eq / 18% FI / 2% cash | 85% eq / 13% FI / 2% cash |
| Aggressive | 60% eq / 30% FI / 10% cash | 75% eq / 20% FI / 5% cash | 90% eq / 10% FI / 0% cash | 95–100% eq / 0–5% FI / 0% cash |

**Adjustments based on other profile factors:**

- **Capacity for loss is lower than stated tolerance** (e.g., aggressive tolerance but moderate capacity): Shift one column toward conservative. The crash reaction reveals more than the self-assessment.
- **Income objective:** Even with aggressive risk tolerance, include some income-generating allocation (dividend equities, bonds, REITs).
- **High liquidity needs:** Increase cash or short-duration bond allocation by 5–10%.
- **Variable income stability:** Keep a larger cash buffer (5–10% more than baseline).

### Geographic Equity Allocation

A reasonable starting point for equity sub-allocation by region. Adjust based on the investor's home country, conviction, and constraints.

| Region | Global Market Cap Weight (approx.) | Suggested Range | Notes |
|--------|-----------------------------------|-----------------|-------|
| US | ~60% | 30–60% | Dominant market; home bias for US investors pushes higher. Non-US investors may want less to avoid currency concentration. |
| Europe | ~15% | 5–25% | Home bias for European investors. Underweight if no specific conviction. |
| Emerging Markets | ~10% | 5–25% | Higher growth potential, higher volatility. Scale with risk tolerance and time horizon. |
| Asia-Pacific (Developed) | ~8% | 0–15% | Japan, Australia, Singapore. Often captured via "Global ex-US" funds. |
| Global ex-US | — | 0–40% | Alternative to breaking out Europe/EM/APAC individually. Simpler, fewer positions. |

**Home bias consideration:** Investors naturally overweight their home market. A German investor might tilt 10–15% toward Europe, which is reasonable but should be conscious, not accidental.

### Portfolio Structure Templates

Choose based on the investor's stated preference and contribution size.

#### Core / Satellite

The most common structure for investors who want broad market exposure plus thematic conviction.

- **Core (50–70% of portfolio):** Broad, diversified, low-cost index exposure. This is the anchor that provides market returns.
- **Satellite (30–50% of portfolio):** Thematic, high-conviction, or tactical positions. These express the investor's views on macro themes, sectors, or individual companies.
- **Tactical tilt budget:** Typically 100% of the satellite bucket is available for thematic allocation. Alternatively, some investors prefer to keep part of the satellite in diversified factor exposure (value, momentum, quality) and only tilt a portion toward themes.

Best for: Investors with €1,000+/month contributions who want to express views beyond passive indexing.

#### Single-Tier (Simple Diversified)

All positions serve the same purpose — broad diversification. No thematic tilts.

- Typically 3–6 ETFs covering major regions and asset classes
- Rebalancing is straightforward (target weights, contribution allocation)

Best for: Beginners, small contribution amounts (< €500/month), or investors who want a fully passive approach.

#### Barbell

Concentrate at two extremes: very safe (government bonds, cash) and very aggressive (growth stocks, thematic ETFs). Nothing in the middle.

- **Safe end (30–50%):** Short-duration government bonds, money market
- **Aggressive end (50–70%):** Concentrated growth equities, thematic ETFs

Best for: Investors who are comfortable with high volatility on part of the portfolio but want guaranteed stability on the rest. Unusual for beginners.

#### Factor-Based

Allocate by factor tilts (value, momentum, quality, size, low volatility) rather than pure geography.

- Requires more positions and more nuanced rebalancing
- Higher complexity, potentially higher risk-adjusted returns

Best for: Experienced investors who understand factor investing and want systematic exposure.

---

## Conflict Detection Rules

Check these after drafting a proposal and after every user modification. If a conflict fires, raise it conversationally — don't block, just inform.

### 1. Conservative profile with 0% fixed income

**Trigger:** Risk tolerance is Conservative or Moderate-Conservative AND the proposed allocation has 0% fixed income.

**Message:** "Your risk profile leans conservative, which typically includes some fixed income for stability. A 0% bond allocation means your portfolio will move entirely with the stock market — including full exposure to drawdowns. If that's intentional, no problem, but I want to make sure it's a conscious choice."

### 2. Short horizon with high equity

**Trigger:** Time horizon < 5 years AND equity allocation > 60%.

**Message:** "With a horizon under 5 years, a heavy equity position carries meaningful risk — a market downturn might not have time to recover before you need the money. Consider whether a more conservative split would better protect your timeline."

### 3. Aggressive tolerance but moderate/low capacity

**Trigger:** Stated risk tolerance is Aggressive or Moderate-Aggressive BUT capacity for loss is Moderate or Low (based on crash reaction).

**Message:** "There's a gap between your stated risk tolerance and how you said you'd react to a crash. This is very common — most people overestimate their comfort with drawdowns until they experience one. I'd suggest we plan for a slightly more moderate allocation. You can always increase equity exposure later as you build confidence."

### 4. Income objective without income allocation

**Trigger:** Primary objective is Income AND the proposed allocation has no fixed income, no dividend-focused equity, and no REITs.

**Message:** "Your goal is income, but the current allocation is entirely growth-focused with no income-generating positions. To generate regular income, we'd typically include some combination of dividend-focused equities, bonds, or REITs. Would you like to adjust?"

### 5. Too many positions for contribution size

**Trigger:** Monthly contribution < €1,000 AND the proposed allocation has > 6 distinct slots.

**Message:** "With €[amount]/month, spreading across [N] positions means each one gets a very small monthly purchase. This can create practical issues — some brokerages have minimum order sizes, and small positions are harder to rebalance. Consider simplifying to 4–6 positions, or using broader funds that cover multiple regions in one holding."

### 6. Liquidity needs not reflected

**Trigger:** Liquidity needs are Moderate or High AND cash allocation is 0%.

**Message:** "You mentioned you might need access to some of this money. The current allocation has no cash buffer. Consider setting aside 5–15% in cash or very short-term bonds so you don't have to sell equities at a bad time if something comes up."

---

## Sub-Allocation Guidelines

### Equity Style (within each geographic region)

| Primary Objective | Suggested Equity Style |
|------------------|----------------------|
| Growth | Blend or Growth tilt |
| Income | Value or Dividend-focused |
| Preservation | Low-volatility or Blend |
| Balanced | Blend |

For most investors, **Blend** (broad market index) is the right default for core positions. Growth or value tilts belong in satellites or factor allocations.

### Fixed Income Sub-Allocation (when applicable)

| Risk Tolerance | Duration | Credit Quality | Notes |
|---------------|----------|---------------|-------|
| Conservative | Short to intermediate (1–5y) | High (government, investment-grade) | Prioritize capital preservation |
| Moderate | Intermediate (3–7y) | Mix of government and corporate | Balance yield and stability |
| Aggressive (with bonds) | Longer duration OK | Can include high-yield | If bonds are included despite aggressive risk, they're for diversification — can take more duration risk |

### Tactical Tilt Budget Sizing

The tilt budget determines how much of the portfolio can deviate from the strategic baseline to express macro-driven views.

| Portfolio Structure | Typical Tilt Budget | Where It Lives |
|-------------------|--------------------|----|
| Core/Satellite | 100% of satellite (satellite IS the tilt) | Satellite bucket |
| Single-Tier | 10–20% of total portfolio | Carved from regional allocation |
| Barbell | 100% of aggressive end | Aggressive bucket |
| Factor-Based | 15–25% for thematic overlay | Separate from factor allocations |

---

## Practical Sizing Guidelines

These help keep the allocation manageable based on how much the investor is putting in each month.

| Monthly Contribution | Max Recommended Positions | Structure Suggestion |
|---------------------|--------------------------|---------------------|
| < €300 | 2–3 | Single global ETF + 1 satellite or bond |
| €300–€700 | 3–5 | Simple single-tier or core (2) + satellite (1–2) |
| €700–€1,500 | 5–8 | Core/satellite works well |
| €1,500–€3,000 | 6–10 | Full core/satellite with regional breakdown |
| €3,000+ | 8–12 | Full multi-bucket with geographic and thematic detail |

These are guidelines, not limits. A €500/month investor can have 8 positions if they're fine with small monthly allocations per position — but flag it as a consideration.

---

## Experienced User Fast-Track

If the user is experienced and provides a direct allocation specification (e.g., "60/40 equities/bonds, core/satellite with 55/45 split"), accept it directly:

1. Parse their specification into the structured format
2. Fill in any gaps with reasonable defaults (e.g., if they say "core/satellite 60/40" but don't specify geographic splits, propose them)
3. Run conflict checks against their profile
4. Present the complete proposal for confirmation
5. Write the file

Don't force experienced users through a long explanation cycle. They know what they want — your job is to structure it, check for conflicts, and fill gaps.

---

## Output Template

The final `asset-allocation.md` must follow this structure. Adapt the sections based on what the proposal includes (e.g., skip Fixed Income section if there are no bonds).

```markdown
# Strategic Asset Allocation

*Created: YYYY-MM-DD | Last updated: YYYY-MM-DD*

## Strategy

[Core / Satellite | Single-Tier | Barbell | Factor-Based]

## Top-Level Allocation

| Asset Class | Target % |
|-------------|----------|
| Equities | [X]% |
| Fixed Income | [X]% |
| Alternatives | [X]% |
| Cash | [X]% |

## Core Bucket — [X]% of total portfolio

**Purpose:** [What this bucket does — e.g., broad market exposure, portfolio anchor, geographic diversification]

| Region | Target % of Core | Style |
|--------|-----------------|-------|
| [Region] | [X]% | [Blend / Growth / Value] |
| ... | ... | ... |

## Satellite Bucket — [X]% of total portfolio

**Purpose:** [What this bucket does — e.g., thematic / high-conviction positions aligned with macro themes]

- **Tactical tilt budget:** [X]% of satellite bucket
- Sub-allocation to be determined after macro research (Stage 3) and security selection (Stage 4)

## Fixed Income — [X]% of total portfolio

**Purpose:** [What bonds are doing — stability, income, rebalancing buffer]

| Type | Target % of FI | Duration | Credit Quality |
|------|---------------|----------|---------------|
| [Government / Corporate / etc.] | [X]% | [Short / Intermediate / Long] | [High / Investment-grade / etc.] |
```

### Notes on the template

- Skip the **Fixed Income** section entirely if the allocation is 0% bonds.
- Skip the **Satellite Bucket** section if using a single-tier structure (replace with just the equity sub-allocation).
- For a **Barbell** structure, use "Safe Bucket" and "Aggressive Bucket" instead of "Core" and "Satellite".
- For **Factor-Based**, list factor allocations instead of geographic regions.
- The satellite sub-allocation details are intentionally left for later stages (macro research and security selection will fill them in). Only include the satellite sizing and purpose at this point.
- All percentages within a bucket should sum to 100% of that bucket. Top-level allocation should sum to 100%.
