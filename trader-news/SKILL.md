---
name: trader-news
description: News Monitor for Indian Equities (NSE/BSE). Tracks breaking news, corporate announcements, order wins, and earnings events in Indian Standard Time (IST).
---

# /trader-news — Indian Stock Market News Monitor

Tracks breaking financial headlines, regulatory disclosures, contract awards, and earnings reports on your Indian watchlist:
- Scrapes Indian financial headlines (Moneycontrol, Economic Times, Livemint, Business Standard, CNBC-TV18).
- Automatically tags headlines: `[EARNINGS]`, `[DEAL/ORDER]`, `[REGULATORY]`, `[CORPORATE_ACTION]`.
- Displays all timestamps in **IST (Indian Standard Time)**.
- Enforces the golden day-trading rule: if earnings or major board meetings are scheduled today, reminds you to be flat before 15:15 IST.

## Usage

```bash
# Track news across active watchlist for the last 12 hours
python3 trader-news/news.py --tickers RELIANCE,TCS,TATAMOTORS --hours 12

# Check breaking headlines on a single stock
python3 trader-news/news.py --tickers HDFCBANK --hours 6
```
