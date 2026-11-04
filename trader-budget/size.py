#!/usr/bin/env python3
"""
trader-budget/size.py
Budget & Position Sizing Manager for Indian Equities.
Sizes orders in INR (₹) based on max risk per trade, whole-share constraints,
and Indian broker MIS margin requirements.
Writes order to trader/orders.json.
"""

import argparse
import json
import math
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from trader.common import (
    DEFAULT_CONFIG_PATH, DEFAULT_PLAN_PATH, DEFAULT_ORDERS_PATH,
    load_config, format_inr, now_ist
)

def size_position(
    max_loss_inr: float = None,
    capital_inr: float = None,
    write: bool = True
) -> dict:
    config = load_config()

    # Read plan from trader/plan.json
    if not os.path.exists(DEFAULT_PLAN_PATH):
        raise FileNotFoundError(f"Plan file not found at {DEFAULT_PLAN_PATH}. Run /trader-exit first.")

    with open(DEFAULT_PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    symbol = plan["symbol"]
    direction = plan.get("direction", "BUY")
    entry_price = plan["entry_price"]
    stop_loss = plan["stop_loss"]
    target_price = plan["target_price"]
    risk_per_share = plan["risk_per_share"]

    account_capital = capital_inr if capital_inr is not None else config.get("account_capital_inr", 100000.0)
    max_loss = max_loss_inr if max_loss_inr is not None else config.get("max_loss_per_trade_inr", 1000.0)

    # Calculate exact whole shares (NSE cash equities allow only whole integer shares)
    shares = math.floor(max_loss / risk_per_share)
    if shares < 1:
        shares = 1

    actual_max_loss = round(shares * risk_per_share, 2)
    trade_value = round(shares * entry_price, 2)
    potential_profit = round(shares * abs(target_price - entry_price), 2)

    # Intraday MIS margin requirement (~20% margin / 5x leverage for liquid NSE stocks)
    mis_mult = config.get("mis_leverage_multiplier", 5.0)
    margin_required = round(trade_value / mis_mult, 2)

    order_payload = {
        "symbol": symbol,
        "exchange": "NSE",
        "direction": direction,
        "product": "MIS", # Margin Intraday Square-off
        "order_type": "LIMIT",
        "quantity": shares,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": target_price,
        "risk_per_share_inr": risk_per_share,
        "total_max_loss_inr": actual_max_loss,
        "potential_gain_inr": potential_profit,
        "trade_value_inr": trade_value,
        "margin_required_inr": margin_required,
        "account_capital_inr": account_capital,
        "max_loss_budget_inr": max_loss,
        "status": "PENDING_RISK_CHECK",
        "created_at_ist": now_ist().strftime("%Y-%m-%d %H:%M:%S IST")
    }

    result = {
        "orders": [order_payload],
        "summary": {
            "symbol": symbol,
            "quantity": shares,
            "capital_inr": account_capital,
            "max_loss_budget_inr": max_loss,
            "actual_max_loss_inr": actual_max_loss,
            "trade_value_inr": trade_value,
            "margin_required_inr": margin_required
        }
    }

    if write:
        os.makedirs(os.path.dirname(DEFAULT_ORDERS_PATH), exist_ok=True)
        with open(DEFAULT_ORDERS_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return result

def main():
    parser = argparse.ArgumentParser(description="Budget & Position Sizing Manager for Indian Equities")
    parser.add_argument("--max-loss", type=float, help="Max loss budget in INR for this trade")
    parser.add_argument("--capital", type=float, help="Account capital in INR")
    parser.add_argument("--write", action="store_true", default=True, help="Write order to trader/orders.json")

    args = parser.parse_args()

    try:
        res = size_position(max_loss_inr=args.max_loss, capital_inr=args.capital, write=args.write)
        ord_info = res["orders"][0]

        print("\n" + "=" * 76)
        print(f"POSITION SIZING & BUDGET: {ord_info['symbol']} ({ord_info['direction']})")
        print("=" * 76)
        print(f"Account Capital:      {format_inr(ord_info['account_capital_inr'])}")
        print(f"Max Loss Budget:      {format_inr(ord_info['max_loss_budget_inr'])}")
        print(f"Risk per Share:       {format_inr(ord_info['risk_per_share_inr'])}")
        print(f"Quantity (Whole Qty): {ord_info['quantity']} shares")
        print(f"Total Trade Value:    {format_inr(ord_info['trade_value_inr'])}")
        print(f"Intraday MIS Margin:  {format_inr(ord_info['margin_required_inr'])} (~5x leverage)")
        print(f"Actual Loss at Stop:  {format_inr(ord_info['total_max_loss_inr'])} (within budget)")
        print(f"Potential Gain:       {format_inr(ord_info['potential_gain_inr'])}")
        print("-" * 76)
        print(f"Bracket Order: {ord_info['direction']} {ord_info['quantity']} {ord_info['symbol']} @ {format_inr(ord_info['entry_price'])}, SL: {format_inr(ord_info['stop_loss'])}, Target: {format_inr(ord_info['take_profit'])}")
        print("=" * 76)
        if args.write:
            print(f"[OK] Orders saved to: {DEFAULT_ORDERS_PATH}")
            print(">> Next step: Run '/trader-risk' to pass strict risk management gatekeepers.")
        print("")

    except Exception as e:
        print(f"[ERROR] Failed to size position: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
