---
name: trader-exit
description: Exit Planner for Indian Equities (NSE/BSE). Sets stop-loss, profit target, and mandatory 15:15 IST intraday square-off before you enter. Writes trader/plan.json.
---

# /trader-exit — Indian Stock Market Exit Planner

Calculates your predetermined exit points before entering a trade:
- **Stop-Loss**: Uses Opening Range Midpoint (`or-mid`), Opening Range Low (`or-low`), or custom risk points.
- **Profit Target**: 1R (1x Risk), 1.5R, or 2R.
- **Strict Intraday Square-off**: Mandates **15:15 IST** flat cutoff. Indian brokers auto-square off MIS intraday orders at 3:15-3:25 PM with penalty fees; exiting at 15:15 IST keeps you in total control.
- Persists the plan into `trader/plan.json`.

## Usage

```bash
# Plan an exit using OR Midpoint stop and 1R target (writes trader/plan.json)
python3 trader-exit/exit.py --symbol RELIANCE --entry 1364.18 --stop or-mid --target 1R --write

# Plan a 1.5R target with custom opening range levels
python3 trader-exit/exit.py --symbol TCS --entry 3890.00 --or-high 3875.00 --or-low 3840.00 --or-mid 3857.50 --target 1.5R --write
```
