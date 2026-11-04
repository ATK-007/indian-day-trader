---
name: trader-broker
description: Order Executor for Indian Equities (NSE/BSE). Stages and executes orders with Zerodha Kite, Angel One, Upstox, or Paper Broker. Never trades without explicit human 'yes'.
---

# /trader-broker — Indian Stock Market Broker Order Executor

Prepares and executes orders across popular Indian brokerage interfaces:
- **Brokerage Payloads**: Formats standard API JSON for **Zerodha Kite Connect**, **Angel One SmartAPI**, **Upstox**, and **Dhan**.
- **Paper Trading by Default**: `paper: true` is standard. Writes simulated executions to `trader/paper_trades.json` without risking a single Rupee.
- **Indian Statutory Charges**: Accurately estimates STT (Securities Transaction Tax), Stamp Duty, NSE Exchange turnover charges, SEBI fees, and GST.
- **THE SAFETY IRONCLAD RULE**:
  Nothing is ever placed automatically. You must inspect the ticket and explicitly confirm (`--confirm-yes` or typing "yes" in chat).

## Usage

```bash
# Inspect staged tickets in plain English
python3 trader-broker/ticket.py show

# Execute staged paper order with explicit confirmation
python3 trader-broker/ticket.py execute --confirm-yes
```
