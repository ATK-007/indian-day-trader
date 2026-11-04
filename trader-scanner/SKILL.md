---
name: trader-scanner
description: Chart Scanner for Indian Equities (NSE/BSE). Scans thousands of stocks for opening-range breakouts (ORB), VWAP crosses, and pre-market setups.
---

# /trader-scanner — Indian Stock Market Chart Scanner

Scans Indian equity charts (NSE NIFTY 50, NIFTY NEXT 50, and F&O liquid universe) for intraday momentum setups:
- **15-minute / 30-minute Opening Range Breakouts (ORB)**: 09:15 to 09:30 AM or 09:45 AM IST.
- **VWAP Crossovers**: Price breaking through intraday Volume Weighted Average Price with volume expansion.
- **Pre-Market Daily Setups**: Gap-up / Gap-down screening and daily key level pivots.

All tools run pure standard-library Python reading free public data (Yahoo Finance `.NS` feeds and NSE indices).

## Usage

```bash
# Display the tracked liquid NSE universe
python3 trader-scanner/scan.py universe

# Scan for 15-minute Opening Range Breakouts at 10:15 AM IST
python3 trader-scanner/scan.py orb --at 10:15

# Scan 30-minute Opening Range Breakouts across top 20 stocks
python3 trader-scanner/scan.py orb --at 10:30 --mins 30 --limit 20

# Scan for intraday VWAP momentum crossovers
python3 trader-scanner/scan.py vwap

# Scan pre-market gaps and daily key levels
python3 trader-scanner/scan.py daily
```

## How It Works in an Indian Trading Session
1. **09:15 AM IST**: NSE bell rings. The stock trades inside its opening range.
2. **09:30 AM IST**: The 15-minute Opening Range (High, Low, Midpoint) is locked in.
3. **10:15 AM IST**: Running `/trader-scanner` identifies which stocks have confirmed a 5-minute candle close above the opening range high (Bullish ORB) or below opening range low (Bearish ORB).
4. Feed the best candidate (e.g. `RELIANCE` or `TCS`) into `/trader-news` and `/trader-entry`.
