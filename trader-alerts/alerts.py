#!/usr/bin/env python3
"""
trader-alerts/alerts.py
Price and Market Clock Alerts for Indian Equities.
Monitors price targets, stop losses, and Indian trading session milestones:
- 09:15 IST: Opening Bell
- 09:30 IST: Opening Range Established
- 15:10 IST: Auto-Square-off 5-Minute Warning
- 15:15 IST: Mandatory Intraday Square-off
- 15:30 IST: NSE Closing Bell
"""

import argparse
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from trader.common import (
    DEFAULT_ALERTS_PATH, DEFAULT_PLAN_PATH, fetch_yahoo_chart,
    format_inr, now_ist, clean_symbol
)

def load_alerts() -> list:
    if os.path.exists(DEFAULT_ALERTS_PATH):
        try:
            with open(DEFAULT_ALERTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_alerts(alerts: list):
    os.makedirs(os.path.dirname(DEFAULT_ALERTS_PATH), exist_ok=True)
    with open(DEFAULT_ALERTS_PATH, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

def add_from_plan():
    if not os.path.exists(DEFAULT_PLAN_PATH):
        print(f"[ERROR] Plan file not found at {DEFAULT_PLAN_PATH}. Run /trader-exit first.", file=sys.stderr)
        sys.exit(1)

    with open(DEFAULT_PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    alerts = load_alerts()
    sym = plan["symbol"]

    # Target Alert
    alerts.append({
        "id": f"ALERT-TP-{len(alerts)+1}",
        "type": "PRICE_ABOVE" if plan["direction"] == "BUY" else "PRICE_BELOW",
        "symbol": sym,
        "price": plan["target_price"],
        "message": f"TARGET HIT: {sym} reached take-profit target {format_inr(plan['target_price'])}",
        "status": "ACTIVE",
        "created_at": now_ist().strftime("%Y-%m-%d %H:%M:%S IST")
    })

    # Stop Loss Alert
    alerts.append({
        "id": f"ALERT-SL-{len(alerts)+1}",
        "type": "PRICE_BELOW" if plan["direction"] == "BUY" else "PRICE_ABOVE",
        "symbol": sym,
        "price": plan["stop_loss"],
        "message": f"STOP HIT: {sym} touched stop-loss {format_inr(plan['stop_loss'])}",
        "status": "ACTIVE",
        "created_at": now_ist().strftime("%Y-%m-%d %H:%M:%S IST")
    })

    # Mandatory 15:15 IST Time Alert
    alerts.append({
        "id": f"ALERT-TIME-{len(alerts)+1}",
        "type": "TIME_EQUALS",
        "symbol": sym,
        "time_ist": "15:15",
        "message": f"INTRADAY CUTOFF: 15:15 IST hit. Flatten all remaining {sym} MIS positions immediately!",
        "status": "ACTIVE",
        "created_at": now_ist().strftime("%Y-%m-%d %H:%M:%S IST")
    })

    save_alerts(alerts)
    print(f"\n[OK] Added 3 alerts from plan for {sym} (Target, Stop, and 15:15 IST Square-off).")

def check_alerts(simulated_price: float = None, simulated_time: str = None):
    alerts = load_alerts()
    if not alerts:
        print("No active alerts configured. Use 'alerts.py add --from-plan' to add.")
        return

    curr_time = simulated_time or now_ist().strftime("%H:%M")
    print(f"\n[Alert Engine] Checking alerts at {curr_time} IST...")

    triggered_count = 0
    for a in alerts:
        if a["status"] != "ACTIVE":
            continue

        triggered = False
        if a["type"] == "TIME_EQUALS" and a.get("time_ist") == curr_time:
            triggered = True
        elif a["type"] in ["PRICE_ABOVE", "PRICE_BELOW"]:
            price = simulated_price
            if price is None:
                res = fetch_yahoo_chart(a["symbol"], interval="5m", range_str="1d")
                price = res.get("regularMarketPrice", a["price"])

            if a["type"] == "PRICE_ABOVE" and price >= a["price"]:
                triggered = True
            elif a["type"] == "PRICE_BELOW" and price <= a["price"]:
                triggered = True

        if triggered:
            triggered_count += 1
            a["status"] = "TRIGGERED"
            a["triggered_at_ist"] = curr_time
            print("\n" + "*" * 68)
            print(f"*** ALERT TRIGGERED [{a['id']}]: {a['message']} ***")
            print("*" * 68 + "\n")

    save_alerts(alerts)
    if triggered_count == 0:
        print("All monitored alerts are steady (none triggered).")

def list_alerts():
    alerts = load_alerts()
    print("\n" + "=" * 76)
    print(f"{'ALERT ID':<16} {'SYMBOL':<10} {'TYPE':<14} {'TRIGGER':<14} {'STATUS':<12}")
    print("=" * 76)
    for a in alerts:
        val = format_inr(a.get("price", 0.0)) if "price" in a else a.get("time_ist", "-")
        print(f"{a['id']:<16} {a['symbol']:<10} {a['type']:<14} {val:<14} {a['status']:<12}")
    print("=" * 76 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Price & Clock Alerts for Indian Equities")
    subparsers = parser.add_subparsers(dest="command")

    add_p = subparsers.add_parser("add", help="Add alerts")
    add_p.add_argument("--from-plan", action="store_true", help="Load alerts from active trade plan")

    check_p = subparsers.add_parser("check", help="Check alerts once")
    check_p.add_argument("--price", type=float, help="Simulate current market price")
    check_p.add_argument("--time", help="Simulate current IST time (e.g. 15:15)")

    subparsers.add_parser("list", help="List all alerts")

    args = parser.parse_args()

    if args.command == "add":
        if args.from_plan:
            add_from_plan()
    elif args.command == "check":
        check_alerts(simulated_price=args.price, simulated_time=args.time)
    elif args.command == "list":
        list_alerts()
    else:
        list_alerts()

if __name__ == "__main__":
    main()
