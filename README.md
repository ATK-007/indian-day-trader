# 🇮🇳 Indian Day Trader: 11 Claude Skills for Indian Stock Market (NSE & BSE)

> **Scan thousands of Indian charts, track breaking corporate news, time every entry and exit with 5-minute bar precision, and replay every outcome 10,000 times before you risk a single Rupee (₹).**

Free, MIT, no signup, no API key required. Built with plain Python standard library reading free public data: Yahoo Finance Indian charts (`.NS`), NSE liquid universes (NIFTY 50, NIFTY NEXT 50, and F&O liquid equities), Google News India RSS, and SEBI PIT (Prohibition of Insider Trading) filings & NSE Bulk Deals.

- **One scans thousands of Indian charts** for opening-range breakouts, flags, and VWAP crosses.
- **Another tracks breaking corporate headlines** on every stock you watch in Indian Standard Time (IST) and flags earnings risks.
- **One watches a setup bar by bar** and tells you the moment to enter (confirmed 5-minute candle close).
- **Another sets your stop and target before you enter**, including a strict **15:15 IST** auto-squareoff cutoff to prevent broker MIS penalty fees.
- **The Time Machine**: before you risk a single Rupee, it replays the rest of the Indian trading session 10,000 times from the stock's recent 5-minute bars, plus trailing real sessions where the setup fired, and tells you the honest odds.
- **And no trade goes through until you say yes.** Nothing in this pack places an order on its own. Paper trading is the default.

---

## The Eleven Skills

| Command | Skill | What It Does in Indian Markets |
|---|---|---|
| `/trader-scanner` | **Chart Scanner** | Scans liquid NSE/BSE stocks for 15m/30m Opening-Range Breakouts (ORB), VWAP crossovers, and pre-market gaps. |
| `/trader-news` | **News Monitor** | Tracks breaking corporate news, order wins, and SEBI notices in **IST**; flags quarterly earnings dates. |
| `/trader-entry` | **Entry Timer** | Watches 5-minute candles bar by bar; triggers only on confirmed candle closes between 09:30 and 14:30 IST. |
| `/trader-exit` | **Exit Planner** | Sets your stop-loss, profit target (1R, 1.5R, 2R), and mandatory **15:15 IST** intraday auto-squareoff. |
| `/trader-timemachine` | **Time Machine** | Replays 10,000 simulated Indian sessions plus trailing 59-day setup history before you risk capital. |
| `/trader-budget` | **Budget Manager** | Sizes positions in **₹ (INR)** based on risk budget; enforces whole shares (no fractional shares) and MIS margin. |
| `/trader-risk` | **Risk Manager** | Enforces hard limits: max loss, daily loss cap, reward-to-risk ratio, entry windows, and NSE circuit filters. |
| `/trader-broker` | **Order Executor** | Generates tickets for Zerodha Kite, Angel One, Upstox, Dhan, or Paper Trading. **Never trades without your explicit "yes"**. |
| `/trader-alerts` | **Price & Clock Alerts** | Rings on target, stop, 09:15 opening bell, 15:10 warning, and 15:15 mandatory MIS auto-squareoff. |
| `/trader-analyst` | **Earnings Analyst** | Analyzes quarterly results (Q1–Q4), PAT, EBITDA, YoY growth, and valuation multiples in ₹ Crores. |
| `/trader-insider`<br>*(alias `/trader-pelosi`)* | **SEBI & Bulk Deals Tracker** | Tracks SEBI Regulation 7(2) promoter buying, insider filings, and daily 3:45 PM NSE/BSE Bulk & Block deals. |

---

## Installation & Setup

### For Claude / Claude Code / Antigravity

Copy the `trader-*` folders directly into your skills directory:

```bash
# Global installation in Claude:
cp -r trader-* ~/.claude/skills/

# Or project-local installation:
mkdir -p .claude/skills
cp -r trader-* .claude/skills/
```

### Pure Python CLI Tools
Requires **Python 3.8+** standard library. **Zero `pip install` dependencies required.**

```bash
# 1. Chart Scanner: Universe and Opening Range Breakouts
python3 trader-scanner/scan.py universe
python3 trader-scanner/scan.py orb --at 10:15
python3 trader-scanner/scan.py vwap

# 2. News Monitor: Real-time headlines in IST
python3 trader-news/news.py --tickers RELIANCE,TCS,TATAMOTORS --hours 12

# 3. Entry Timer: Bar-by-bar trigger check
python3 trader-entry/entry.py check RELIANCE --setup orb
python3 trader-entry/entry.py watch RELIANCE --every 30

# 4. Exit Planner: Stop, target, and 15:15 IST cutoff
python3 trader-exit/exit.py --symbol RELIANCE --entry 1364.18 --stop or-mid --target 1R --write

# 5. Time Machine: 10,000 Monte Carlo replays + 59-day history
python3 trader-timemachine/timemachine.py run --write
python3 trader-timemachine/timemachine.py chart

# 6. Budget Manager: Risk-adjusted INR sizing (whole shares)
python3 trader-budget/size.py --max-loss 50 --write

# 7. Risk Manager: Rigorous audit (PASS or BLOCK)
python3 trader-risk/check.py

# 8. Order Broker: Plain English ticket + Paper Execution
python3 trader-broker/ticket.py show
python3 trader-broker/ticket.py execute --confirm-yes

# 9. Alerts: Target, Stop, and 15:15 IST clock
python3 trader-alerts/alerts.py add --from-plan
python3 trader-alerts/alerts.py check

# 10. Financial Analyst: Corporate quarterly results
python3 trader-analyst/facts.py RELIANCE

# 11. Insider & Bulk Deal Tracker:
python3 trader-insider/insider.py --ticker RELIANCE
python3 trader-insider/insider.py --deals bulk
```

---

## How It Works: The Complete Indian Market Trade Workflow

Everything lands in a `trader/` folder in your project, and each skill reads what the last one wrote:

```
scanner -> news -> entry -> exit -> timemachine -> budget -> risk -> broker (one trade)
alerts: stop, target, flat by 15:15 IST (while trade is open)
news / analyst / insider (on a schedule or as needed)
```

### Walkthrough Example: Reliance Industries (RELIANCE) on NSE

1. **`/trader-scanner` at 10:15 AM IST**:
   Of the liquid NSE universe scanned, the 15-minute Opening Range (09:15 to 09:30 AM IST) for `RELIANCE` was **₹1,354.47 to ₹1,362.18** (midpoint ₹1,358.32). The 10:10 5-minute candle closed at **₹1,364.18** (+0.55% over range high).
2. **`/trader-news`**:
   Checks breaking headlines in IST: *"Reliance Retail expands quick-commerce footprint across 50 top cities ahead of festive push"*. Confirms no board meeting or earnings report today—safe for intraday trading.
3. **`/trader-entry`**:
   Watched RELIANCE bar by bar. At 10:12 it reported `waiting` (10:10 candle was still forming). At 10:15 it reported `triggered`: confirmed 5-minute close at **₹1,364.18**.
4. **`/trader-exit`**:
   Sets the plan before entry:
   - Stop-loss at OR midpoint: **₹1,358.32** (₹5.86 per share risk).
   - Target at 1R: **₹1,370.04** (+₹5.86 gain).
   - Cutoff: **15:15:00 IST** mandatory square-off. Writes to `trader/plan.json`.
5. **`/trader-timemachine`**:
   Replays the rest of the day until 15:15 IST 10,000 times using historical 5-minute return distributions from previous 59 sessions (seed 19):
   - Target hit first: **29.4%**
   - Stop hit first: **25.5%**
   - Still open at 15:15 IST cutoff: **45.1%**
   - Trailing 59 real sessions: setup fired 33 times (13 hit target, 15 hit stop, 5 flat).
   - Verdict: Close to a coin flip. Reality check before risking capital!
6. **`/trader-budget`**:
   With a ₹5,000 account and a ₹50 max loss per trade:
   - Shares: `floor(50 / 5.86) = 8 shares` (trade value: ₹10,913.44).
   - If stop fills at ₹1,358.32, loss is **₹46.88** (within ₹50 budget).
   - Intraday MIS margin required: ~₹2,182.68 (5x leverage). Writes `trader/orders.json`.
7. **`/trader-risk`**:
   Evaluates 6 rules: Max loss check, RRR (1:1), entry window (10:15 IST inside 09:30–14:30), MIS margin coverage, and NSE circuit buffer. Output: **PASS**.
8. **`/trader-broker`**:
   Displays the ticket with itemized Indian statutory charges (STT, Stamp Duty, GST, Exchange fees). Prompts for explicit confirmation: `type yes`. In paper mode, logs fill in `trader/paper_trades.json`.
9. **`/trader-alerts`**:
   Rings when price hits ₹1,370.04, ₹1,358.32, or at **15:15 IST** to close remaining position.

---

## Indian Stock Market Fine Print & Rules

1. **Not Financial Advice**:
   This software reads public data and calculates arithmetic. Most retail day traders lose money in Indian markets (per SEBI studies, >90% of individual intraday traders incur net losses). Trade responsibly and paper trade first.
2. **Mandatory 15:15 IST Square-off**:
   Indian discount brokers (Zerodha, Angel One, Upstox, Groww) automatically square off open MIS intraday positions between 15:15 and 15:25 IST and levy an auto-squareoff charge (typically ₹50 + 18% GST). `/trader-exit` enforces a 15:15 IST cutoff so you retain full control over your execution.
3. **No PDT Rule in India**:
   Unlike the US, SEBI does not enforce a minimum capital requirement like the Pattern Day Trader (PDT) rule. You can day trade with any capital size. However, SEBI enforces **Peak Margin Regulations**, requiring ~20% upfront margin for equity intraday MIS trades.
4. **NSE Price Bands & Circuit Filters**:
   NSE cash stocks operate under 5%, 10%, or 20% price bands. Getting caught in a circuit halt can result in shares going to exchange physical auction with heavy penalties. `/trader-risk` checks circuit distance to safeguard against auction risk.
5. **Statutory Taxes in India**:
   Equity intraday profits are taxed as Speculative Business Income under the Indian Income Tax Act. Every transaction attracts STT (Securities Transaction Tax), Stamp Duty, NSE Turnover Charges, SEBI Regulatory fees, and 18% GST.
6. **Paper First**:
   `"paper": true` is the default in `trader/config.json`. Live trading connectors require explicit human confirmation for every single order.
