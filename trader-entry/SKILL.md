---
name: trader-entry
description: Entry Timer for Indian Equities (NSE/BSE). Watches setups bar by bar and triggers only on confirmed candle closes during Indian market trading windows.
---

# /trader-entry — Indian Stock Market Entry Timer

Watches an intraday setup bar by bar and confirms the exact moment to enter:
- **Bar-by-bar confirmation**: Never enters while a 5-minute candle is still forming. A candle close is mandatory.
- **Time window gating**: Validates entries between 09:30 AM and 14:30 PM IST (avoids the midday lull).
- Returns explicit status: `waiting` (candle still forming or inside range), `triggered` (confirmed candle close), or `expired`.

## Usage

```bash
# Check if an Opening Range Breakout has triggered for RELIANCE
python3 trader-entry/entry.py check RELIANCE --setup orb

# Simulate check at 10:12 IST (during candle formation)
python3 trader-entry/entry.py check RELIANCE --at 10:05

# Watch bar by bar every 30 seconds
python3 trader-entry/entry.py watch RELIANCE --every 30
```
