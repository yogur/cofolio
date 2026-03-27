# CoFolio — Your AI-Powered Portfolio Advisor 📈

CoFolio is a plugin for [Cowork](https://claude.com/product/cowork) (Anthropic's collaborative workspace) that guides you through building and maintaining a personal investment portfolio, from scratch to a fully analyzed, rebalanceable portfolio.

Think of it as having a knowledgeable financial advisor on call who walks you through every step: understanding your goals, researching the market, picking investments, checking for blind spots, and keeping things on track over time.

**Who it's for:** Anyone who wants to invest but doesn't know where to start, *and* experienced investors who want a structured, repeatable process. No finance degree required.

> **Disclaimer:** CoFolio is an educational tool, not a licensed financial advisor. Nothing it produces constitutes financial advice. Always do your own research.

## Quick Start

### Prerequisites

- Claude Desktop
- Python 3.10+

### Install the plugin

1. Open the Claude Desktop app.
2. Switch to the **Cowork** tab at the top.
3. Click **Customize** in the left sidebar, then **Browse plugins**.
4. Select **Personal**, click the **+** button, and choose **Add marketplace from GitHub**.
5. Enter the repository URL: `https://github.com/yogur/cofolio`
6. Once added, enable CoFolio from your plugin list.

<details>
<summary>Also installable via Claude Code</summary>

```bash
/plugin marketplace add yogur/cofolio
/plugin install cofolio@cofolio-marketplace
```
</details>

### Start building your portfolio

Open Cowork in any empty directory (this becomes your portfolio workspace):

```
/portfolio-advisor
```

CoFolio takes it from there. It'll ask about your financial situation, research the markets, help you pick investments, and produce a full portfolio report — all as a guided conversation.

## What CoFolio Does

CoFolio walks you through a structured, multi-stage process that mirrors how professional advisors build portfolios. Each stage produces a file in your workspace, so you always have a clear record of decisions made and why.

### 1. Investor Profile

CoFolio starts by getting to know you: your age, income, risk tolerance, goals, and any constraints (like ethical preferences or brokerage limitations). This shapes every decision that follows.

### 2. Strategic Asset Allocation

Based on your profile, CoFolio proposes how to split your money across asset classes (equities, bonds, etc.) and regions. You can accept, tweak, or ask for alternatives. It explains the trade-offs in plain language.

### 3. Macro Research

An AI research agent scans current market conditions (monetary policy, geopolitics, technology trends, sector rotations) and presents investable themes. You pick the ones that resonate with your convictions.

### 4. Security Selection

Another AI agent screens for specific instruments (ETFs, stocks) that match your allocation and themes. It compares candidates side by side so you can make informed picks.

### 5. Portfolio Construction & Analysis

CoFolio assigns weights to your selections and then runs the numbers:

- **Overlap analysis:** Are you accidentally overexposed to a single stock through multiple ETFs?
- **Fee drag:** How much will fund expenses cost you over 10, 20, or 30 years?
- **Concentration check:** Is your portfolio too heavy in one country or sector?

You review the results and adjust until you're comfortable.

### 6. Report

Everything is compiled into a comprehensive portfolio report: your profile, the rationale, what to buy, how much, and an action plan for your monthly contributions.

### 7. Ongoing Maintenance

Markets move. CoFolio helps you stay on track with drift analysis and rebalancing recommendations, telling you exactly where to direct your monthly contributions to keep your portfolio aligned with your targets.

## Commands

| Command | What it does |
|---------|-------------|
| `/portfolio-advisor` | Your single entry point for everything: start or resume a portfolio build, check status, run a rebalance check, or do standalone macro research |

## Under the Hood

CoFolio is built from modular components. Here's what powers each part of the experience:

### Skills

| Skill | Role |
|-------|------|
| Portfolio Advisor | Single orchestrator: detects intent and pipeline stage, loads the relevant stage reference file, and guides you through every step from profiling to maintenance |

### AI Research Agents

| Agent | Role |
|-------|------|
| Macro Researcher | Goes online to investigate current macro conditions across 6 categories |
| Security Screener | Searches for and evaluates specific ETFs, stocks, and bonds matching your criteria |

### Analysis Scripts

| Script | Role |
|--------|------|
| Overlap analysis | Detects hidden single-stock concentration across your ETF holdings |
| Fee analysis | Projects the long-term cost of fund expenses on your portfolio |
| Concentration analysis | Maps your true geographic and sector exposure |
| Drift analysis | Measures how far your current portfolio has drifted from targets |
| Rebalancing optimizer | Calculates how to allocate contributions to minimize drift without selling |

## License

MIT
