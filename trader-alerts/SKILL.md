---
name: trader-alerts
description: Price Alerts & Clock Manager for Indian Equities (NSE/BSE). Rings when a target, stop loss, or 15:15 IST intraday auto-squareoff milestone hits. Writes trader/alerts.json.
---

# /trader-alerts — Indian Stock Market Price & Time Alerts

Rings notifications on key intraday price levels and Indian market clock milestones:
- **Automatic Setup from Plan**: Automatically creates alerts for Take-Profit target, Stop-Loss, and the 15:15 IST flat-by-close mandate.
- **Indian Market Milestones**:
  - `09:15 IST`: Opening Bell
  - `09:30 IST`: Opening Range High/Low Established
  - `15:10 IST`: 5-Minute Warning before broker auto-squareoff
  - `15:15 IST`: Mandatory Intraday Square-off
- Stores alert states in `trader/alerts.json`.

## Usage

```bash
# Add alerts directly from current trade plan
python3 trader-alerts/alerts.py add --from-plan

# List all active alerts
python3 trader-alerts/alerts.py list

# Check alerts against current market price or time
python3 trader-alerts/alerts.py check

# Test time-trigger at 15:15 IST
python3 trader-alerts/alerts.py check --time 15:15
```
