---
name: trader-risk
description: Risk Manager for Indian Equities (NSE/BSE). Checks staged orders against hard risk limits: max loss, daily loss cap, entry windows, and margin before broker staging.
---

# /trader-risk — Indian Stock Market Risk Manager

The uncompromising gatekeeper that evaluates every planned trade against strict Indian market constraints:
- **Max Loss per Trade**: Guarantees actual stop loss does not exceed your limit.
- **Reward-to-Risk**: Rejects any trade with poor asymmetry.
- **Entry Window**: Restricts entries strictly to 09:30 AM – 14:30 PM IST (prohibits entries too close to the 15:15 IST auto-squareoff).
- **Margin & Capital Audit**: Verifies account cash vs. MIS margin requirements.
- **NSE Price Band / Circuit Buffer**: Protects you from getting locked into upper/lower circuit halts that lead to exchange auction penalties.
- Outputs `PASS` or `BLOCK` with explicit reasons.

## Usage

```bash
# Audit staged orders in trader/orders.json
python3 trader-risk/check.py

# Simulate check during morning trading window at 10:15 IST
python3 trader-risk/check.py --sim-time 10:15
```
