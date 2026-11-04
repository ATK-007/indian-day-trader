---
name: trader-timemachine
description: Time Machine for Indian Equities (NSE/BSE). Replays 10,000 simulated trading sessions and tests historical setup occurrences before risking a single Rupee. Writes trader/timemachine.json.
---

# /trader-timemachine — Indian Market Intraday Time Machine

Replays every possible outcome of a day trade before you risk real money:
- **10,000 Monte Carlo Replays**: Takes the stock's 5-minute bar volatility distribution over the previous 59 sessions and simulates 10,000 remainder-of-session trajectories up to the **15:15 IST** cutoff.
- **Historical Backtest**: Re-runs the exact same setup rule across the stock's last 59 actual trading days to reveal its true historical win rate.
- **Honest Odds Verdict**: Gives you the unvarnished probability of hitting the Target First, Stop First, or ending up flat by 15:15 IST.
- Includes an ASCII Trajectory Fan Chart and writes results to `trader/timemachine.json`.

## Usage

```bash
# Run 10,000 replays using the plan saved in trader/plan.json
python3 trader-timemachine/timemachine.py run --write

# Run on custom trade parameters
python3 trader-timemachine/timemachine.py run --symbol RELIANCE --entry 1364.18 --stop 1358.32 --target 1370.04 --write

# View the ASCII Fan Chart of trajectory percentiles
python3 trader-timemachine/timemachine.py chart
```
