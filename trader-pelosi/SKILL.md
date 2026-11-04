---
name: trader-pelosi
description: Indian Market equivalent of the Pelosi / Congressional Tracker. Monitors SEBI insider disclosures, promoter open-market buying, and NSE/BSE daily bulk deals.
---

# /trader-pelosi — Indian Market Insider & Institutional Deal Tracker

In the Indian stock market, the direct equivalent of Congressional / STOCK Act disclosures is **SEBI Prohibition of Insider Trading (PIT) Regulation 7(2)** and **Daily NSE/BSE Bulk & Block Deals**.

This skill tracks:
- Promoters buying shares directly from the open market.
- Institutional block deals by FIIs (Foreign Institutional Investors) and DIIs (Mutual Funds, LIC).
- Superstar Indian investors' bulk deals.

## Usage

```bash
# Query recent disclosures (maps to Indian SEBI/Bulk deal tracker)
python3 trader-pelosi/ptr.py index --member promoter

# Filter for a specific Indian stock
python3 trader-pelosi/ptr.py --ticker RELIANCE
```
