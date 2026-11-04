#!/usr/bin/env python3
"""
trader-broker/ticket.py
Order Executor for Indian Equities (NSE/BSE).
Generates execution tickets for Indian brokers (Zerodha Kite, Angel One, Upstox, Dhan)
and paper trading engine.
SAFETY RULE: No order is EVER submitted without explicit confirmation ("yes").
Paper trading is the default.
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
    DEFAULT_CONFIG_PATH, DEFAULT_ORDERS_PATH, DEFAULT_PAPER_PATH,
    load_config, format_inr, now_ist
)

def calculate_indian_statutory_charges(trade_value: float, is_intraday: bool = True) -> dict:
    """
    Calculate realistic Indian market statutory transaction charges:
    - STT (Securities Transaction Tax): 0.025% on sell side for equity intraday
    - Exchange Turnover Charges (NSE): ~0.00297%
    - SEBI Turnover Charges: ~0.0001%
    - Stamp Duty: 0.003% on buy side
    - GST: 18% on (brokerage + exchange charges + SEBI charges)
    - Brokerage: ₹20 flat or 0.03% (e.g. Zerodha / Angel One discount broker model)
    """
    brokerage = min(20.0, trade_value * 0.0003)
    stt = trade_value * 0.00025 if is_intraday else trade_value * 0.001
    exchange_charges = trade_value * 0.0000297
    sebi_charges = trade_value * 0.000001
    stamp_duty = trade_value * 0.00003
    gst = (brokerage + exchange_charges + sebi_charges) * 0.18
    total_charges = round(brokerage + stt + exchange_charges + sebi_charges + stamp_duty + gst, 2)

    return {
        "brokerage": round(brokerage, 2),
        "stt": round(stt, 2),
        "exchange_charges": round(exchange_charges, 2),
        "stamp_duty": round(stamp_duty, 2),
        "gst": round(gst, 2),
        "total_estimated_charges": total_charges
    }

def format_broker_payload(order: dict, broker: str) -> dict:
    """Format payload according to specific Indian broker API standards."""
    sym = order["symbol"]
    qty = order["quantity"]
    price = order["entry_price"]
    sl = order["stop_loss"]
    tp = order["take_profit"]

    if broker == "zerodha":
        return {
            "broker": "Zerodha Kite Connect",
            "api_endpoint": "https://api.kite.trade/orders/regular",
            "payload": {
                "tradingsymbol": sym,
                "exchange": "NSE",
                "transaction_type": order["direction"],
                "order_type": "LIMIT",
                "quantity": qty,
                "price": price,
                "product": "MIS", # Margin Intraday Square-off
                "validity": "DAY",
                "tag": "IndianDayTrader"
            },
            "bracket_legs": {
                "stoploss": sl,
                "squareoff": tp
            }
        }
    elif broker == "angelone":
        return {
            "broker": "Angel One SmartAPI",
            "api_endpoint": "https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/placeOrder",
            "payload": {
                "variety": "NORMAL",
                "tradingsymbol": f"{sym}-EQ",
                "symboltoken": "00000",
                "transactiontype": order["direction"],
                "exchange": "NSE",
                "ordertype": "LIMIT",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": price,
                "quantity": qty
            }
        }
    else: # Default paper trading
        return {
            "broker": "Simulated Paper Broker (Indian Market)",
            "mode": "PAPER_TRADING",
            "order": order
        }

def show_ticket():
    if not os.path.exists(DEFAULT_ORDERS_PATH):
        print(f"[ERROR] Orders file not found at {DEFAULT_ORDERS_PATH}. Run /trader-budget first.", file=sys.stderr)
        sys.exit(1)

    with open(DEFAULT_ORDERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    orders = data.get("orders", [])
    if not orders:
        print("[ERROR] No orders staged.", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    broker = config.get("broker", "zerodha")
    is_paper = config.get("paper", True)

    print("\n" + "=" * 76)
    print("ORDER EXECUTION TICKET — STAGED FOR BROKER CONFIRMATION")
    print("=" * 76)

    for i, ord_info in enumerate(orders):
        charges = calculate_indian_statutory_charges(ord_info["trade_value_inr"])
        broker_spec = format_broker_payload(ord_info, broker)

        print(f"Ticket ID:        IN-ORD-{i+1:04d}")
        print(f"Mode:             {'[PAPER TRADING - NO REAL MONEY]' if is_paper else '[LIVE BROKER TRADING]'}")
        print(f"Broker Target:    {broker_spec['broker']}")
        print(f"Exchange:         {ord_info['exchange']}")
        print(f"Contract / Stock: {ord_info['symbol']} (NSE Equity)")
        print(f"Action:           {ord_info['direction']} {ord_info['quantity']} shares")
        print(f"Product Type:     MIS (Intraday - auto-square off by 15:15 IST)")
        print(f"Order Type:       LIMIT @ {format_inr(ord_info['entry_price'])}")
        print(f"Stop-Loss:        {format_inr(ord_info['stop_loss'])}")
        print(f"Take-Profit:      {format_inr(ord_info['take_profit'])}")
        print(f"Total Value:      {format_inr(ord_info['trade_value_inr'])}")
        print(f"Margin Needed:    {format_inr(ord_info['margin_required_inr'])} (approx 5x leverage)")
        print(f"Govt & Brokerage: ~{format_inr(charges['total_estimated_charges'])} (STT, Stamp Duty, GST, Exchange)")
        print(f"Risk Audit State: {ord_info['status']}")
        print("-" * 76)

    print("SAFETY GATE: Nothing can be placed until you explicitly confirm.")
    print("To execute this order in paper mode, confirm with: --confirm-yes")
    print("=" * 76 + "\n")

def execute_ticket(confirm_yes: bool = False):
    if not confirm_yes:
        print("[BLOCKED] Execution aborted. Confirmation flag '--confirm-yes' was not provided.")
        return

    with open(DEFAULT_ORDERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    orders = data.get("orders", [])
    config = load_config()

    paper_trades = []
    if os.path.exists(DEFAULT_PAPER_PATH):
        try:
            with open(DEFAULT_PAPER_PATH, "r", encoding="utf-8") as f:
                paper_trades = json.load(f)
        except Exception:
            paper_trades = []

    executed_count = 0
    for ord_info in orders:
        if ord_info["status"] != "PASSED_RISK_CHECK":
            print(f"[SKIP] Order {ord_info['symbol']} has not passed risk check (Status: {ord_info['status']}).")
            continue

        fill_record = {
            "trade_id": f"PAPER-NSE-{len(paper_trades) + 1:05d}",
            "symbol": ord_info["symbol"],
            "direction": ord_info["direction"],
            "quantity": ord_info["quantity"],
            "fill_price": ord_info["entry_price"],
            "stop_loss": ord_info["stop_loss"],
            "take_profit": ord_info["take_profit"],
            "product": "MIS",
            "exchange": "NSE",
            "filled_at_ist": now_ist().strftime("%Y-%m-%d %H:%M:%S IST"),
            "status": "OPEN",
            "simulated": True
        }
        paper_trades.append(fill_record)
        executed_count += 1
        ord_info["status"] = "FILLED"

    with open(DEFAULT_PAPER_PATH, "w", encoding="utf-8") as f:
        json.dump(paper_trades, f, indent=2)

    with open(DEFAULT_ORDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("\n" + "=" * 76)
    print(f"[SUCCESS] {executed_count} Order(s) executed in PAPER TRADING mode.")
    print(f"Log written to: {DEFAULT_PAPER_PATH}")
    print(">> Next step: Run '/trader-alerts' to monitor stop, target, and 15:15 IST cutoff.")
    print("=" * 76 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Order Ticket & Broker Executor for Indian Markets")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("show", help="Display staged order ticket details")

    exec_p = subparsers.add_parser("execute", help="Execute order with explicit confirmation")
    exec_p.add_argument("--confirm-yes", action="store_true", help="Explicit human confirmation to place order")

    args = parser.parse_args()

    if args.command == "show":
        show_ticket()
    elif args.command == "execute":
        execute_ticket(confirm_yes=args.confirm_yes)
    else:
        show_ticket()

if __name__ == "__main__":
    main()
