---
name: trader-budget
description: Budget Manager for Indian Equities (NSE/BSE). Sizes every position to your INR risk budget, enforces whole-share integer quantities, and handles MIS margin requirements. Writes trader/orders.json.
---

# /trader-budget — Indian Stock Market Budget & Position Sizer

Sizes every position mathematically in Indian Rupees (₹) to safeguard your capital:
- **Exact Risk Sizing**: `shares = floor(max_loss / risk_per_share)`.
- **Whole-Share Integrity**: Respects NSE cash equity rules where fractional shares do not exist.
- **MIS Margin Calculator**: Applies SEBI intraday margin norms (~5x leverage / 20% margin on liquid NSE stocks).
- Generates the complete bracket order specifications and saves them into `trader/orders.json`.

## Usage

```bash
# Size position using settings in trader/config.json and trader/plan.json
python3 trader-budget/size.py --write

# Custom max loss budget of ₹500 for this trade
python3 trader-budget/size.py --max-loss 500 --write

# Custom account capital of ₹50,000 with ₹50 max loss
python3 trader-budget/size.py --capital 50000 --max-loss 50 --write
```
