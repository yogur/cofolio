# Report Generation — Reference Material

This file contains the report template, section-by-section specifications, formatting standards, and example sections. Read this before writing `report.md`.

---

## Report Template

Use this structure for every report. All sections are required — if a section has no content (e.g., empty watchlist), include the heading with a brief note rather than omitting it.

```markdown
# Portfolio Report

*Generated: YYYY-MM-DD | Data as of: YYYY-MM-DD*

## 1. Executive Summary
## 2. Investor Profile
## 3. Macro Landscape
## 4. Portfolio Breakdown
### Core Bucket — X% of portfolio
### Satellite Bucket — Y% of portfolio
## 5. Analysis Highlights
### Stock-Level Exposure
### Geographic Allocation
### Sector Allocation
### Fee Impact
## 6. Action Plan
### Initial Purchase Order
### Monthly Contribution Strategy
## 7. Risk Factors
## 8. Watchlist
```

---

## Section Specifications

### 1. Executive Summary

The executive summary is a standalone snapshot — someone reading only this section should understand the portfolio's structure, rationale, and next steps.

**Include:**
- Portfolio structure in one sentence (e.g., "Core/satellite, 100% equities, N positions")
- Total number of positions and split across buckets
- Weighted average TER
- Top 1-2 conviction themes (from selected macro themes)
- The single most important insight from the analysis (e.g., "NVIDIA is your largest single-stock exposure at X% across 3 instruments")
- Immediate next step (e.g., "Execute the buy list below via XETRA on Scalable Capital")

**Length:** 6-10 lines. This is a summary — resist the urge to include everything.

**Example:**

```markdown
## 1. Executive Summary

This portfolio follows a core/satellite strategy with 100% equity allocation across 8 positions. The core bucket (55%) provides broad market exposure through low-cost index ETFs. The satellite bucket (45%) expresses three macro themes: AI infrastructure, European defense, and emerging market growth.

Weighted average TER is 0.19% — competitive for the level of thematic exposure. The main concentration risk is NVIDIA at 4.8% of total portfolio, appearing through three instruments. This is intentional given the AI thesis but worth monitoring.

Monthly contributions of €3,500 should be allocated across all positions using the contribution strategy in Section 6. Execute initial purchases via XETRA on Scalable Capital.
```

### 2. Investor Profile

A concise recap of the parameters that shaped the portfolio. Not a copy of `investor-profile.md` — just the fields that matter for understanding the portfolio decisions.

**Include (as a bullet list or compact table):**
- Age, country, currency
- Risk tolerance and time horizon
- Monthly contribution amount (and range if specified)
- Primary objective
- Key constraints (brokerage, exchange requirements, ethical exclusions)
- Portfolio structure preference

**Example:**

```markdown
## 2. Investor Profile

| Parameter | Value |
|-----------|-------|
| Age / Horizon | 32 / ~25 years |
| Country / Currency | Germany / EUR |
| Risk tolerance | Aggressive |
| Monthly contribution | €3,500 (range: €3,000–4,000) |
| Objective | Growth |
| Brokerage | Scalable Capital (XETRA) |
| Constraints | UCITS, accumulating preferred |
| Structure | Core / Satellite |
```

### 3. Macro Landscape

Summarize each selected macro theme and map it to the portfolio positions that express it. The reader should understand the connection between the thesis and what they own.

**For each selected theme, include:**
- Theme name and category
- 2-3 sentence thesis summary (from `macro-themes.md`)
- Time horizon (structural vs. cyclical)
- Confidence level
- Which portfolio positions express this theme (with ticker and weight)
- Key risk or invalidation trigger

**Group themes logically** — by category or by portfolio bucket. Don't just list them in the order they appear in `macro-themes.md`.

**Example:**

```markdown
## 3. Macro Landscape

*Research date: 2026-03-22*

### AI Infrastructure Boom (Technology) — High Confidence

AI server spending is projected to jump 45% in 2026 to $312B. The shift from training to inference broadens demand across the semiconductor value chain — not just GPU makers but memory, packaging, EUV lithography, and power infrastructure.

**Portfolio expression:**
- VanEck Semiconductor ETF (SMH) — 15.0%
- ASML Holding (ASML) — 5.0%

**Time horizon:** Structural (multi-year)
**Key risk:** Valuation compression if capex guidance disappoints. Invalidated if AI spending growth decelerates below 20% YoY.

### European Rearmament (Geopolitics) — High Confidence

EU has outlined an €800B defense plan. Europe has collectively underspent on defense by ~€850B. Defense spending growth of ~5% expected in 2026, projected as a multi-year structural cycle.

**Portfolio expression:**
- iShares Europe Defence ETF (EDEF) — 10.0%

**Time horizon:** Structural (multi-year)
**Key risk:** Peace dividend if conflicts de-escalate. Invalidated if EU defense spending growth falls below 3%.
```

### 4. Portfolio Breakdown

The most detailed section. Show every position grouped by bucket, with enough detail that the user can understand what they own and why.

**For each position, include:**

| Field | Source |
|-------|--------|
| Instrument name | `instrument.name` |
| Ticker / ISIN | `instrument.ticker` / `instrument.isin` |
| Exchange | `instrument.exchange` |
| Type | `instrument.type` (ETF, stock) |
| Weight | `target_weight_pct` |
| TER | `instrument.ter_pct` (ETFs only; stocks have no TER) |
| Hypothesis | `hypothesis` field |

**Format as a summary table per bucket, followed by per-position detail blocks:**

```markdown
## 4. Portfolio Breakdown

### Core Bucket — 55% of Portfolio

**Purpose:** Broad market exposure, portfolio anchor, geographic diversification

| # | Instrument | Ticker | Weight | TER |
|---|-----------|--------|--------|-----|
| 1 | iShares Core S&P 500 UCITS ETF | SXR8 | 19.25% | 0.07% |
| 2 | Vanguard FTSE All-World ex-US | VXUS | 16.50% | 0.08% |
| 3 | iShares Core MSCI Europe | IMEU | 5.50% | 0.12% |
| 4 | iShares Core MSCI EM IMI | IS3N | 13.75% | 0.18% |

**1. iShares Core S&P 500 UCITS ETF (SXR8) — 19.25%**
ISIN: IE00B5BMR087 | XETRA | Physical | Accumulating
*Broad US large-cap exposure as portfolio anchor. Low-cost market-cap-weighted index provides diversified US equity beta.*

**2. Vanguard FTSE All-World ex-US (VXUS) — 16.50%**
...

### Satellite Bucket — 45% of Portfolio

**Purpose:** Thematic / high-conviction positions aligned with macro themes

| # | Instrument | Ticker | Weight | TER | Theme |
|---|-----------|--------|--------|-----|-------|
| 5 | VanEck Semiconductor ETF | SMH | 15.00% | 0.35% | AI Infrastructure |
| 6 | ASML Holding | ASML | 5.00% | — | AI Infrastructure |
| 7 | iShares Europe Defence | EDEF | 10.00% | 0.50% | European Rearmament |
...
```

**For individual stocks with valuation data** (`valuation_snapshot` is not null), add a compact valuation line:

```markdown
**6. ASML Holding (ASML) — 5.00%**
ISIN: NL0010273215 | XETRA | Stock
P/E (fwd): 28.1 | PEG: 1.4 | FCF Yield: 2.8% | Analyst consensus: 22 Buy / 5 Hold / 1 Sell (PT €820)
*Captures the AI infrastructure thesis — semiconductor equipment is a bottleneck in the AI buildout. ASML has near-monopoly on EUV lithography.*
```

### 5. Analysis Highlights

Present the analysis data from `portfolio.json`'s `analysis` section with interpretation. The numbers alone aren't useful — help the user understand what they mean for their portfolio.

**Four subsections, each structured as: data → interpretation → context.**

#### Stock-Level Exposure

Source: `analysis.top_stock_exposures`

Show the top exposures table and flag any stock above 3% of total portfolio. For flagged stocks, explain whether the concentration is intentional (user's thematic bet) or accidental (ETF overlap).

```markdown
### Stock-Level Exposure

| Stock | Total Exposure | Sources |
|-------|---------------|---------|
| NVIDIA (NVDA) | 4.8% | SXR8 (1.2%) + SMH (3.1%) + direct? |
| Apple (AAPL) | 3.9% | SXR8 (1.4%) + VXUS (0.8%) + ... |
| Microsoft (MSFT) | 3.7% | SXR8 (1.3%) + ... |

NVIDIA's 4.8% exposure is the portfolio's highest single-stock concentration. This is an intentional consequence of the AI infrastructure thesis (S&P 500 exposure + dedicated semiconductor ETF). Monitor if NVDA exceeds 6% — at that point the concentration risk outweighs the thematic benefit.
```

Where possible, reconstruct the source breakdown for flagged stocks. For each ETF that holds the stock: the stock's weight within the ETF (from `top_holdings`) multiplied by the ETF's portfolio weight gives the contribution. Direct stock positions contribute at their full `target_weight_pct`. This helps the user understand *where* the concentration comes from.

#### Geographic Allocation

Source: `analysis.geographic_split`

Show the geographic breakdown and compare it to any targets in `asset-allocation.md`. Note significant tilts.

```markdown
### Geographic Allocation

| Region | Portfolio Weight |
|--------|-----------------|
| US | 52% |
| Europe | 18% |
| Emerging Markets | 15% |
| Asia Developed | 10% |
| Other | 5% |

The portfolio has a US tilt at 52%, driven by the S&P 500 core position and the US-heavy semiconductor sector. This is consistent with the allocation target and the AI infrastructure thesis (most AI leaders are US-listed).
```

#### Sector Allocation

Source: `analysis.sector_split`

Same format as geographic. Flag any sector above 30% — it's likely an intentional thematic bet but worth noting.

```markdown
### Sector Allocation

| Sector | Portfolio Weight |
|--------|-----------------|
| Technology | 35% |
| Financials | 12% |
| Healthcare | 10% |
| Industrials | 10% |
| Consumer Discretionary | 8% |
| Other | 25% |

Technology is the dominant sector at 35%, a direct result of the AI infrastructure satellite positions layered on top of tech-heavy US index exposure. This is intentional but creates meaningful sector concentration risk — a broad tech selloff would hit this portfolio harder than a market-cap-weighted benchmark.
```

#### Fee Impact

Source: `analysis.weighted_avg_ter_pct`, `analysis.fee_drag_*`

Present the weighted average TER with context (low/moderate/high) and the fee drag projections. Fee drag numbers represent the cumulative cost of fees over time compared to a zero-fee hypothetical — the money "lost" to fund expenses.

```markdown
### Fee Impact

**Weighted average TER:** 0.19%

| Horizon | Fee Drag |
|---------|----------|
| 10 years | €2,850 |
| 20 years | €12,400 |
| 30 years | €28,400 |

*Assumes 7% annual growth, €3,500/month contributions, €0 initial value.*

A 0.19% weighted TER is competitive for a portfolio with thematic satellite exposure. The core ETFs average 0.09% while the satellite ETFs (semiconductor, defense) pull the average up with TERs of 0.35-0.50%. Over 30 years, the fee drag of €28,400 represents about X% of the projected portfolio value — a meaningful but manageable cost for the thematic exposure.
```

To express fee drag as a percentage of projected value, compute it: `fee_drag_Ny / (projected_value_Ny) * 100`. The projected value can be estimated from the contribution and growth assumptions. If you can't compute it precisely, omit the percentage and just present the absolute number.

### 6. Action Plan

This section turns the report from analysis into instructions. It should be specific enough that the user can execute it without referring back to other documents.

**Two subsections:**

#### Initial Purchase Order

For a new portfolio (first report), list every instrument in execution order. Order by:
1. Core positions first (these are the foundation)
2. Within each bucket, largest weight first
3. If the user has a lump sum, all at once. If DCA-ing, note the schedule.

```markdown
### Initial Purchase Order

Execute these purchases on Scalable Capital via XETRA:

| # | Instrument | Ticker | ISIN | Weight | Amount* |
|---|-----------|--------|------|--------|---------|
| 1 | iShares Core S&P 500 | SXR8 | IE00B5BMR087 | 19.25% | €674 |
| 2 | iShares Core MSCI EM IMI | IS3N | IE00BKM4GZ66 | 13.75% | €481 |
| ... | ... | ... | ... | ... | ... |

*Amount based on €3,500 monthly contribution allocated by weight.
```

For a rebalancing report (re-generation), show the changes: what to buy, sell, or trim, with amounts.

#### Monthly Contribution Strategy

Show how to split the monthly contribution across positions. This is the ongoing execution plan.

```markdown
### Monthly Contribution Strategy

With €3,500/month, allocate as follows:

| Instrument | Ticker | Weight | Monthly Amount |
|-----------|--------|--------|----------------|
| iShares Core S&P 500 | SXR8 | 19.25% | €674 |
| Vanguard FTSE All-World ex-US | VXUS | 16.50% | €578 |
| iShares Core MSCI EM IMI | IS3N | 13.75% | €481 |
| VanEck Semiconductor ETF | SMH | 15.00% | €525 |
| ... | ... | ... | ... |
| **Total** | | **100%** | **€3,500** |

Round to whole euros in practice — small rounding differences wash out over time. If your brokerage supports fractional shares, execute exact amounts. Otherwise, round to the nearest share and let small remainders accumulate as cash until they're large enough for a share.
```

**Contribution math:** `monthly_amount = target_weight_pct / 100 × monthly_contribution`. Round to 2 decimal places. If the investor profile specifies a range (e.g., €3,000–4,000), use the stated amount (e.g., €3,500) as the base.

### 7. Risk Factors

Identify 4-6 key risks specific to this portfolio. These should be concrete and tied to the portfolio's actual exposures, not generic market risks.

**For each risk:**
- Name it clearly
- Explain what it would look like (leading indicator)
- Note which positions are most affected
- Suggest a reassessment trigger

**Sources of risk to consider:**
- Macro theme invalidation (from `macro-themes.md` — each theme has invalidation triggers)
- Sector/geographic concentration (from analysis)
- Single-stock concentration (from overlap analysis)
- Interest rate sensitivity (if any bond/rate-sensitive positions)
- Currency risk (positions denominated in non-home currencies)
- Liquidity risk (positions with low AUM)
- Fee risk (expensive satellite positions vs. alternatives)

```markdown
## 7. Risk Factors

**1. Technology sector concentration (35%)**
A broad tech selloff — triggered by regulatory action, margin compression, or sentiment shift — would disproportionately affect this portfolio. The core S&P 500 position (32% tech) and semiconductor satellite amplify tech exposure.
*Monitor:* NASDAQ 100 drawdown >15% from peak. *Reassess:* Consider rotating satellite toward non-tech themes.

**2. AI capex cycle peak**
The AI infrastructure thesis depends on continued spending growth. If major cloud providers signal capex moderation (guidance below 20% YoY growth), the semiconductor positions (SMH + ASML = 20% of portfolio) face valuation risk.
*Monitor:* Quarterly earnings from MSFT, GOOG, AMZN, META — capex guidance. *Reassess:* If two or more signal spending plateaus.

...
```

### 8. Watchlist

Pull from `portfolio.json`'s `watchlist` array. If empty, say so. For each watchlist item:

- Instrument name and identifier
- Why it's being watched (not yet actionable, waiting for entry point, alternative to current position)
- Conditions for promotion to active position

```markdown
## 8. Watchlist

No instruments are currently on the watchlist.

*The watchlist tracks instruments and themes being monitored for potential future inclusion. Items can be added during macro research refreshes or maintenance reviews.*
```

Or with items:

```markdown
## 8. Watchlist

| Instrument | Why Watching | Promotion Trigger |
|-----------|-------------|-------------------|
| iShares Global Clean Energy (ICLN) | Energy transition theme — not yet selected | If EU energy policy shifts create clearer regulatory tailwinds |
| Rheinmetall (RHM) | Defense stock — considered but ETF chosen for diversification | If EDEF underperforms pure defense plays by >10% over 6 months |
```

---

## Formatting Standards

- **Use markdown throughout.** Headers, tables, bold, bullet lists. No HTML.
- **Currency:** Use the investor's currency symbol (e.g., €, $, £) from `investor-profile.md`. Use the same currency consistently throughout.
- **Percentages:** One decimal place for weights and exposures (e.g., 19.3%, 4.8%). Two decimal places for TER (e.g., 0.07%, 0.19%).
- **Dates:** YYYY-MM-DD format.
- **Numbers:** Use comma separators for thousands (e.g., €28,400, not €28400).
- **Tables:** Use markdown tables with alignment. Keep tables readable — if a table has too many columns, split it or use a different format.
- **Headers:** Use `##` for main sections (numbered 1-8) and `###` for subsections.
- **Report header:** Include generation date and the latest `data_as_of_date` from the instruments.
- **Footer:** End with a brief disclaimer noting that this is an informational tool, not financial advice, and data may become stale.

---

## Data Freshness Handling

Include a data note near the top of the report (after the executive summary or in the header):

```markdown
*Data as of: 2026-03-22. Holdings data and valuations are snapshots collected during security screening and may shift over time. Rerun /rebalance to refresh.*
```

If the macro research date in `macro-themes.md` is more than 30 days old from the report generation date, add a staleness warning:

```markdown
> **Note:** Macro research was conducted on [date] — more than 30 days ago. Consider running `/research-macro` to refresh themes before making investment decisions.
```

---

## Report Footer

End every report with:

```markdown
---

*This report was generated by CoFolio on [date]. It is an informational tool to support investment decisions, not personalized financial advice. Market conditions, instrument data, and macro themes change over time — rerun `/rebalance` periodically to keep the portfolio aligned with your goals and current conditions.*
```
