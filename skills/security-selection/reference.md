# Security Selection — Reference Material

This file contains screening brief templates, brokerage constraint reference, ETF and stock evaluation criteria, the data completeness checklist, the `portfolio.json` schema, and instrument selection guidelines. Read this when generating briefs, validating agent results, or writing the output file.

---

## Screening Brief Templates

Use these as starting points for constructing briefs for the security screener subagent. Customize each brief with the specific parameters from the investor's profile and allocation.

### Core ETF Brief Template

```
Screening brief: [Slot name — e.g., "Core / US Large-Cap Blend"]

Find 2-3 UCITS [accumulating|distributing] ETFs that:
- Track [index or market segment — e.g., "S&P 500", "FTSE Developed Europe", "MSCI Emerging Markets"]
- Are listed on [exchange — e.g., XETRA]
- Use physical replication (full or optimized sampling preferred; include synthetic if no physical options exist)
- Have AUM above EUR [threshold — typically 500M for core, 100M for satellite]

Investor context:
- Jurisdiction: [e.g., Germany — UCITS required, accumulating preferred for tax efficiency]
- Brokerage: [e.g., Scalable Capital]
- Exclusions: [e.g., none, or "no fossil fuels"]

Collect ALL of the following for each candidate:
- Full fund name, ISIN, ticker on [exchange], domicile
- TER, AUM, replication method, distribution policy, fund currency, benchmark index
- Top 10-15 holdings with name, ticker, and weight percentage
- Geographic breakdown (percentages summing to ~100%)
- Sector breakdown (percentages summing to ~100%)
- Performance: 1Y, 3Y, 5Y returns
- Tracking error
- Data as-of date

Present a comparison summary at the end if returning 2+ candidates.
```

### Satellite ETF Brief Template

```
Screening brief: [Slot name — e.g., "Satellite / AI Infrastructure"]

Find 2-3 UCITS [accumulating|distributing] ETFs that:
- Focus on [theme/sector — e.g., "semiconductors", "European defense and aerospace", "clean energy"]
- Are listed on [exchange]
- Have AUM above EUR 100M (flag below this but still include if no alternatives)

Theme context:
- Thesis: [from macro-themes.md — e.g., "AI server spending projected to jump 45% in 2026..."]
- Relevant sectors: [from macro-themes.md]
- Relevant regions: [from macro-themes.md]
- Time horizon: [structural/cyclical/tactical]

Investor context:
- Jurisdiction: [value]
- Brokerage: [value]
- Exclusions: [value]

Collect ALL of the following for each candidate:
[same data fields as core brief]

If thematic ETFs are limited, note this and suggest whether individual stocks might better capture the theme.
```

### Individual Stock Brief Template

```
Screening brief: [Slot name — e.g., "Satellite / AI Infrastructure — Individual Stock"]

Screen 2-3 individual stocks that:
- Have direct exposure to [theme — e.g., "AI infrastructure — semiconductor equipment, memory, or foundry"]
- Are listed on [exchange] or available via [brokerage]
- Have market cap above EUR [threshold — typically 10B for satellite positions]

Investment style: [Growth | Value | GARP | Dividend — derive from the theme and investor profile]

Theme context:
- Thesis: [from macro-themes.md]
- Why individual stocks for this slot: [e.g., "No thematic ETF adequately captures the narrow exposure to EUV lithography equipment"]

Investor context:
- Jurisdiction: [value]
- Brokerage: [value]
- Exclusions: [value]
- Existing ETF selections: [list ETFs already selected — for overlap checking]

Collect ALL of the following for each candidate:
- Company name, ISIN, ticker, exchange, sector, industry, market cap
- Full valuation snapshot: P/E (TTM and forward), P/B, EV/EBITDA, PEG, FCF yield, dividend yield, payout ratio, debt/equity, revenue growth (1Y), operating margin
- Analyst consensus: buy/hold/sell counts, average price target, recent rating changes
- Geographic revenue breakdown
- Overlap check against the user's ETF selections
- Value trap assessment (for value-oriented briefs)
- Catalyst assessment (for value/contrarian briefs)
- Data as-of date

Present a comparison summary at the end if returning 2+ candidates.
```

### Fixed Income ETF Brief Template

```
Screening brief: [Slot name — e.g., "Fixed Income / EUR Government Intermediate"]

Find 2-3 UCITS [accumulating|distributing] bond ETFs that:
- Focus on [type — e.g., "EUR government bonds", "global aggregate", "EUR corporate investment-grade"]
- Have duration of [target — e.g., "3-7 years (intermediate)"]
- Have credit quality of [target — e.g., "investment-grade only"]
- Are listed on [exchange]
- Have AUM above EUR 500M

Investor context:
- Jurisdiction: [value]
- Brokerage: [value]

Collect ALL of the following for each candidate:
- Full fund name, ISIN, ticker on [exchange], domicile
- TER, AUM, distribution policy, fund currency, benchmark index
- Effective duration, yield to worst
- Credit quality breakdown (% AAA, AA, A, BBB, below investment-grade)
- Geographic breakdown (percentages)
- Performance: 1Y, 3Y, 5Y returns
- Data as-of date
```

---

## Brokerage Constraint Reference

These are hard filters. An instrument that fails any applicable constraint is not viable.

### UCITS / PRIIP Regulation

| Investor Jurisdiction | Constraint | Impact |
|----------------------|-----------|--------|
| EU / EEA (Germany, France, Netherlands, etc.) | PRIIP/KID regulation requires a Key Information Document | Cannot buy US-domiciled ETFs (SPY, QQQ, VTI, etc.). Must use European-domiciled UCITS equivalents. |
| UK | Similar KID requirement post-Brexit | Same restriction on US-domiciled ETFs for most retail investors |
| Switzerland | Generally no UCITS restriction | Can access both US and European ETFs |
| US | No UCITS relevance | Can buy US-domiciled funds directly |

**Common UCITS equivalents for popular US ETFs:**

| US ETF | What It Tracks | UCITS Equivalent(s) | Notes |
|--------|---------------|---------------------|-------|
| SPY / VOO / IVV | S&P 500 | SXR8 (iShares), VUAA (Vanguard), MEUD (Amundi) | SXR8 is the largest UCITS S&P 500 ETF |
| QQQ | NASDAQ 100 | EQQQ (Invesco), CSNDX (iShares) | |
| VTI | US Total Market | SUSA (iShares MSCI USA), VUAA covers similar | No exact total-market UCITS equivalent |
| VEA / VXUS | International Developed / ex-US | VWRL/VWCE (Vanguard All-World), IWDA (iShares World) | |
| VWO | Emerging Markets | EIMI (iShares EM), AUEM (Amundi EM) | |
| AGG / BND | US Aggregate Bonds | AGGH (iShares Global Aggregate), VAGF (Vanguard) | |

### Exchange Availability

| Brokerage | Primary Exchange | Secondary Exchanges | Notes |
|-----------|-----------------|---------------------|-------|
| Scalable Capital (DE) | XETRA (gettex for savings plans) | — | Most UCITS ETFs list on XETRA. Check gettex for savings plan eligibility. |
| Trade Republic (DE) | Lang & Schwarz | — | More limited ETF selection than XETRA |
| Interactive Brokers | Multiple (XETRA, LSE, Euronext, NYSE, NASDAQ) | Broadest access | Can access most global exchanges |
| DeGiro | XETRA, Euronext Amsterdam, LSE, others | — | Core selection list has reduced fees |
| Vanguard UK | LSE | — | Vanguard funds only for ISA/SIPP |

**Always verify listing on the specific exchange.** Fund providers list their products on multiple exchanges — a fund may exist on LSE but not XETRA, or vice versa.

### Accumulating vs. Distributing — Tax Implications

| Jurisdiction | Recommendation | Reason |
|-------------|----------------|--------|
| Germany | Accumulating strongly preferred | Vorabpauschale mechanism is more tax-efficient than receiving distributions. Distributions trigger immediate taxation. |
| UK (ISA) | Either — no tax difference in ISA | Inside an ISA, accumulating avoids reinvestment hassle. In GIA, distributing may be useful for personal allowance. |
| Netherlands | Accumulating preferred | Box 3 taxation is on notional yield, not actual distributions — accumulating simplifies. |
| US | Distributing is standard (US funds) | US tax system doesn't disadvantage distributions in the same way. |

### Domicile and Withholding Tax

| Underlying Exposure | Best Domicile | Reason |
|--------------------|---------------|--------|
| US equities | Ireland | Ireland-US tax treaty: 15% withholding on US dividends vs. 30% for Luxembourg-domiciled funds |
| European equities | Ireland or Luxembourg | Both work; Ireland slightly preferred for most cases |
| Emerging markets | Ireland | Generally better treaty network |

---

## ETF Evaluation Criteria

Use these criteria when validating agent results and when helping the user compare candidates. Listed in priority order.

### 1. Eligibility (Pass/Fail)

These are binary — a candidate either passes or doesn't:

- UCITS status (if required by jurisdiction)
- Listed on the user's specified exchange
- Accumulating or distributing per investor preference
- AUM above EUR 100M (flag below, but don't auto-reject for satellites)

### 2. Cost Efficiency

| Metric | What It Means | How to Compare |
|--------|--------------|----------------|
| TER | Annual management fee deducted from fund assets | Lower is better, but contextualize: 0.07% for S&P 500 is standard; 0.35% for a niche semiconductor ETF may be the cheapest available |
| Tracking difference | Cumulative deviation from benchmark (TD = fund return - index return) | More meaningful than TER alone — captures all costs including securities lending revenue. Negative TD means the fund beat its benchmark (common with securities lending). |
| Tracking error | Annualized standard deviation of return differences | Lower means more consistent tracking. High TE + low TER may indicate sampling issues. |

### 3. Replication Quality

| Method | Description | Preference |
|--------|------------|------------|
| Physical full | Holds all index constituents | Preferred — most transparent, no counterparty risk |
| Physical optimized (sampling) | Holds a representative subset | Acceptable — watch tracking difference closely |
| Synthetic (swap-based) | Uses derivatives to replicate returns | Note counterparty risk — may track better for some indices (e.g., commodities). Appropriate when physical replication is impractical. |

### 4. Fund Size and Liquidity

| Metric | Threshold | Implication |
|--------|-----------|-------------|
| AUM > EUR 1B | Excellent liquidity | Very tight spreads, near-zero closure risk |
| AUM EUR 500M-1B | Good liquidity | Standard for most core positions |
| AUM EUR 100M-500M | Adequate | Acceptable for satellites; spreads may be wider |
| AUM < EUR 100M | Low liquidity flag | Higher closure risk, wider spreads — flag to user |

### 5. Performance Context

- Compare returns against the benchmark (tracking difference), not in absolute terms
- Compare against peer funds tracking the same or similar index
- 5Y returns are more informative than 1Y for core positions
- For new funds (< 3Y track record), note the limited history

---

## Stock Evaluation Criteria

Use when validating stock candidates from the screener agent.

### Valuation Snapshot — Required Fields

Every stock candidate must have all of these. If any are missing, the screening is incomplete.

| Field | What It Tells You |
|-------|------------------|
| P/E (TTM) | Current earnings valuation — compare to sector median |
| P/E (Forward) | Market's expectation of near-term earnings — lower than TTM suggests growth expected |
| P/B | Asset-based valuation — most useful for financials, industrials, asset-heavy businesses |
| EV/EBITDA | Enterprise value relative to operating earnings — accounts for debt differences between companies |
| PEG | Growth-adjusted P/E — below 1.5 suggests reasonable price for growth rate |
| FCF Yield (%) | Free cash flow relative to market cap — higher is better, above 5% is strong |
| Dividend Yield (%) | Annual dividend relative to price — relevant for income positions |
| Payout Ratio (%) | Dividend as % of earnings — above 75% (non-REIT) is a sustainability concern |
| Debt/Equity | Leverage — above 1.0 warrants scrutiny, above 2.0 is high |
| Revenue Growth (1Y) | Top-line momentum — negative growth for 3+ years is a value trap signal |
| Operating Margin (%) | Profitability — compare to sector. Declining margins signal competitive pressure |

### Overlap Check

For every stock candidate, check whether it appears as a top holding in any ETF the user has already selected (or is considering). This is critical because:

- If NVDA is 6.2% of the user's S&P 500 ETF and they add a direct NVDA position, total NVDA exposure could reach 8-10%
- The overlap check must be quantified: "ASML is already 2.1% of your Europe ETF. Adding a direct position at 5% of total portfolio would bring total ASML exposure to approximately 6.2%."

### Value Trap Signals

Flag these when they appear — they don't disqualify a candidate, but the user should know:

| Signal | What to Look For |
|--------|-----------------|
| Secular decline | Revenue declining 3+ consecutive years, shrinking market |
| Governance issues | Excessive insider selling, frequent management changes, related-party transactions |
| Balance sheet stress | Rising debt/equity, declining interest coverage, approaching debt maturities |
| Accounting quality | Gap between reported earnings and operating cash flow, frequent one-time charges |
| Margin compression | Operating margins declining year-over-year, losing pricing power |

---

## Data Completeness Checklist

Use this to validate agent results before presenting to the user. Every candidate must have these fields. If a field is genuinely unavailable after the agent searched, mark it "Not found — searched [sources]."

### ETF Required Fields

- [ ] Full fund name
- [ ] ISIN
- [ ] Ticker (on user's specified exchange)
- [ ] Exchange listing confirmed
- [ ] Type: "ETF"
- [ ] TER (percentage, 2 decimal places)
- [ ] AUM (EUR millions)
- [ ] Replication method (physical full / physical optimized / synthetic)
- [ ] Distribution policy (accumulating / distributing)
- [ ] Fund domicile (Ireland, Luxembourg, etc.)
- [ ] Fund currency
- [ ] Benchmark index name
- [ ] Top 10-15 holdings with name, ticker, and weight percentage — **CRITICAL: do not proceed without this**
- [ ] Geographic breakdown (percentages summing to ~100%)
- [ ] Sector breakdown (percentages summing to ~100%)
- [ ] Performance: 1Y, 3Y, 5Y returns
- [ ] Tracking error (for index ETFs)
- [ ] Data as-of date

### Stock Required Fields

- [ ] Company name
- [ ] ISIN
- [ ] Ticker
- [ ] Exchange listing confirmed
- [ ] Type: "stock"
- [ ] Market cap (EUR or USD, specify currency)
- [ ] Sector and industry
- [ ] Valuation snapshot (all 11 fields above)
- [ ] Analyst consensus (buy/hold/sell counts, average price target)
- [ ] Geographic revenue breakdown
- [ ] Overlap check against user's selected ETFs
- [ ] Data as-of date

---

## portfolio.json Schema

The output of this stage. All positions are written without weights — those come in Stage 5.

```json
{
  "version": "1.0",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "positions": [
    {
      "bucket": "core | satellite",
      "slot": "descriptive_slot_name (snake_case — e.g., US_blend, emerging_markets, ai_infrastructure)",
      "instrument": {
        "name": "Full instrument name",
        "isin": "XX0000000000",
        "ticker": "TICK",
        "exchange": "XETRA | LSE | etc.",
        "type": "ETF | stock",

        "_comment_etf_fields": "Include these for ETFs only:",
        "ter_pct": 0.07,
        "aum_eur_millions": 85000,
        "replication": "physical | physical_optimized | synthetic",
        "distribution": "accumulating | distributing",
        "benchmark": "Index name",
        "fund_domicile": "Ireland | Luxembourg | etc.",
        "fund_currency": "EUR | USD | etc.",

        "_comment_stock_fields": "Include these for stocks only:",
        "sector": "Technology",
        "industry": "Semiconductor Equipment",
        "market_cap_eur_billions": 280,

        "_comment_shared_fields": "Include for both ETFs and stocks:",
        "top_holdings": [
          { "name": "Company Name", "ticker": "TICK", "weight_pct": 7.1 },
          { "name": "...", "ticker": "...", "weight_pct": 0.0 }
        ],
        "geographic_split": { "US": 60, "Europe": 20, "Asia": 15, "Other": 5 },
        "sector_split": { "Technology": 32, "Healthcare": 12, "Financials": 13, "Other": 43 },
        "data_as_of_date": "YYYY-MM-DD",

        "_comment_valuation": "null for ETFs, populated for stocks:",
        "valuation_snapshot": null
      },
      "target_weight_pct": null,
      "current_holdings": null,
      "hypothesis": null,
      "theme_ids": ["theme_id_snake_case"]
    }
  ],
  "watchlist": [
    {
      "name": "Instrument name",
      "isin": "XX0000000000",
      "ticker": "TICK",
      "type": "ETF | stock",
      "reason": "Why it's on the watchlist — e.g., 'Strong candidate for AI slot but user preferred the ETF approach for now'",
      "slot_context": "Which slot this was considered for"
    }
  ]
}
```

### Schema Notes

- **Remove `_comment_*` fields** from actual output — they are documentation only
- **ETF-specific fields** (`ter_pct`, `aum_eur_millions`, `replication`, `distribution`, `benchmark`, `fund_domicile`, `fund_currency`): include for ETFs, omit for stocks
- **Stock-specific fields** (`sector`, `industry`, `market_cap_eur_billions`): include for stocks, omit for ETFs
- **`top_holdings`**: For ETFs, list the top 10-15 holdings from the fund. For individual stocks, this field should be an empty array `[]` (a single stock doesn't have "holdings")
- **`geographic_split`**: For ETFs, use the fund's geographic breakdown. For stocks, use the company's revenue geographic breakdown (e.g., ASML: `{ "Europe": 30, "Asia": 40, "US": 25, "Other": 5 }`). Revenue geography matters because it reflects actual economic exposure — a Dutch company earning 40% of revenue in Asia has meaningful Asian exposure regardless of its domicile. If revenue geography is unavailable, note this as a data gap rather than defaulting to 100% domicile
- **`sector_split`**: For ETFs, use the fund's sector breakdown. For stocks, use `{ "sector_name": 100 }` since a single stock is in one sector
- **`valuation_snapshot`** for stocks:
  ```json
  {
    "pe_ttm": 32.5,
    "pe_fwd": 28.1,
    "pb": 18.4,
    "ev_ebitda": 25.2,
    "peg": 1.4,
    "fcf_yield_pct": 2.8,
    "dividend_yield_pct": 0.7,
    "payout_ratio_pct": 23,
    "debt_equity": 0.35,
    "revenue_growth_1y_pct": 18,
    "operating_margin_pct": 33,
    "analyst_consensus": {
      "buy": 22, "hold": 5, "sell": 1,
      "avg_price_target": 820.00, "currency": "EUR"
    },
    "as_of_date": "YYYY-MM-DD"
  }
  ```
- **`theme_ids`**: For satellite positions tied to a macro theme, use snake_case identifiers derived from the theme name in `macro-themes.md` (e.g., "AI Infrastructure Boom" becomes `"ai_infrastructure_boom"`). For core positions, use `[]`. A position can be tied to multiple themes.
- **`watchlist`**: Instruments the user liked but didn't select for a position. Preserved for future reference during rebalancing or re-evaluation.

---

## Slot Naming Convention

Slot names should be descriptive and use snake_case. They appear in `portfolio.json` and are referenced in downstream stages.

### Core Slot Names

| Allocation Target | Slot Name |
|-------------------|-----------|
| US large-cap blend | `US_blend` |
| US large-cap growth | `US_growth` |
| US large-cap value | `US_value` |
| Europe blend | `europe_blend` |
| Europe value | `europe_value` |
| Emerging markets blend | `emerging_markets` |
| Asia-Pacific developed | `asia_pacific` |
| Global ex-US | `global_ex_us` |
| Global (all-world) | `global_all_world` |

### Satellite Slot Names

Derive from the theme name. Use snake_case, keep it short but descriptive. Note: slot names are short identifiers for the position; `theme_ids` (in the position object) use the full theme name from `macro-themes.md` converted to snake_case (e.g., `ai_infrastructure_boom`). These are different fields with different purposes.

| Theme | Slot Name |
|-------|-----------|
| AI Infrastructure Boom | `ai_infrastructure` |
| European Rearmament | `european_defense` |
| Nuclear Renaissance | `nuclear_energy` |
| India Growth Story | `india_growth` |
| Semiconductor Cycle | `semiconductors` |

### Fixed Income Slot Names

| Allocation Target | Slot Name |
|-------------------|-----------|
| EUR government intermediate | `eur_govt_bonds` |
| Global aggregate | `global_agg_bonds` |
| EUR corporate investment-grade | `eur_corp_bonds` |
| High yield | `high_yield_bonds` |

---

## Instrument Selection Guidelines

### When to Use ETFs vs. Individual Stocks

| Factor | Favors ETF | Favors Individual Stock |
|--------|-----------|------------------------|
| Position type | Core (always ETFs) | Satellite / high-conviction only |
| Theme specificity | Broad theme with a good ETF available | Very narrow theme no ETF captures (e.g., "EUV lithography" = ASML specifically) |
| Contribution size | Small (< EUR 500/month per position) | Larger — stock positions need meaningful sizing |
| Investor experience | Beginner or intermediate | Experienced — understands single-stock risk |
| Diversification need | High — ETFs provide built-in diversification | User already diversified via core; satellite can be concentrated |
| Stated preference | "ETFs only" in profile | "ETFs and individual stocks" in profile |

### Handling Slot Merges and Splits

Users may want to restructure slots during the selection process:

**Merging:** "I want one global ETF instead of separate US, Europe, and EM"
- Accept this. Use a single all-world ETF (e.g., VWCE) and create one position with slot name `global_all_world`
- Note that this changes the core bucket structure — the user loses fine-grained geographic control but gains simplicity

**Splitting:** "I want separate value and growth for the US slot"
- Accept this. Create two positions: `US_value` and `US_growth`
- Note that this adds complexity and requires the user to manage two positions for one region

**Adding new slots:** "I also want a small position in gold"
- Accept if it fits the allocation. Create a new position (e.g., `gold` in a satellite or alternatives bucket)
- Note that this may require revisiting the asset allocation if gold wasn't in the original plan

In all cases, confirm the restructured plan before screening. If the restructured slots diverge materially from `asset-allocation.md` (e.g., merging three regional slots into one global ETF), update `asset-allocation.md` to reflect the new structure before writing `portfolio.json`. This keeps Stage 5 and later stages aligned with the actual portfolio shape.

### Cross-Slot Overlap Awareness

As selections accumulate, track the overlap picture:

| Overlap Scenario | What to Flag |
|-----------------|-------------|
| S&P 500 ETF + NASDAQ 100 ETF | Heavy overlap in top tech stocks (AAPL, MSFT, NVDA, AMZN, META). Combined tech exposure may reach 40-50%. |
| S&P 500 ETF + individual NVDA position | NVDA is already ~6% of S&P 500. Adding a direct position increases concentration. |
| MSCI World ETF + S&P 500 ETF | World is ~60% US. The user effectively has very high US exposure. |
| Europe ETF + European defense ETF | Defense stocks may appear in both. Check top holdings for overlap. |

Don't block selections based on overlap — flag the implication and let the user decide. The full overlap analysis happens in Stage 5, but catching obvious overlaps early is helpful.
