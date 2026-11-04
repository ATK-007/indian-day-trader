---
name: trader-insider
description: SEBI Insider Trading & Bulk/Block Deal Tracker for Indian Equities (NSE/BSE). Monitors promoter open-market buying, FII/DII institutional trades, and celebrity portfolio filings. (Also available as /trader-pelosi).
---

# /trader-insider (and /trader-pelosi) — Indian Stock Market Insider & Bulk Deals Tracker

Tracks institutional transactions and corporate insider buying/selling in the Indian market:
- **SEBI PIT Regulation 7(2)**: Tracks Promoters, Directors, and Key Management personnel buying/selling shares from the open market.
- **Daily NSE/BSE Bulk & Block Deals**: Discloses transactions involving >0.5% of total company equity (FIIs, DIIs, Mutual Funds, and Ace Investors like Rekha Jhunjhunwala, Ashish Kacholia, Vijay Kedia).
- **High-Conviction Signals**: Flags open-market promoter buying and promoter pledge releases.

## Usage

```bash
# View all recent SEBI insider disclosures and bulk deals
python3 trader-insider/insider.py

# Filter disclosures for a specific stock
python3 trader-insider/insider.py --ticker RELIANCE

# Filter by deal type (bulk deals or promoter actions)
python3 trader-insider/insider.py --deals bulk
python3 trader-insider/insider.py --member promoter

# Compatible alias for US repo command
python3 trader-pelosi/ptr.py --ticker RELIANCE
```
