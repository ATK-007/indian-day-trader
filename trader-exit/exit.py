#!/usr/bin/env python3
"""
trader-exit/exit.py
Exit Planner for Indian Equities.
Calculates stop-loss, profit target, and sets mandatory 15:15 IST intraday cutoff.
Writes plan to trader/plan.json.
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
    DEFAULT_PLAN_PATH, clean_symbol, format_inr, now_ist, load_config
)

def plan_exit(
    symbol: str = "RELIANCE",
    entry_price: float = 1364.18,
    direction: str = "BUY",
    stop_mode: str = "or-mid",
    target_mode: str = "1R",
    or_high: float = 1359.20,
    or_low: float = 1347.00,
    or_mid: float = 1353.10,
    write: bool = True
) -> dict:
    direction = direction.upper()

    # Determine Stop Price
    if stop_mode == "or-mid":
        stop_price = or_mid
    elif stop_mode == "or-low":
        stop_price = or_low if direction == "BUY" else or_high
    elif stop_mode.startswith("pts:"):
        pts = float(stop_mode.split(":")[1])
        stop_price = entry_price - pts if direction == "BUY" else entry_price + pts
    else:
        # Default to or-mid
        stop_price = or_mid

    # Calculate Risk per share
    if direction == "BUY":
        risk_per_share = round(entry_price - stop_price, 2)
    else:
        risk_per_share = round(stop_price - entry_price, 2)

    if risk_per_share <= 0:
        risk_per_share = round(entry_price * 0.005, 2) # fallback 0.5% risk
        stop_price = entry_price - risk_per_share if direction == "BUY" else entry_price + risk_per_share

    # Determine Target Price
    multiplier = 1.0
    if target_mode == "1R":
        multiplier = 1.0
    elif target_mode == "1.5R":
        multiplier = 1.5
    elif target_mode == "2R":
        multiplier = 2.0
    elif target_mode.startswith("R:"):
        multiplier = float(target_mode.split(":")[1])

    target_distance = round(risk_per_share * multiplier, 2)
    if direction == "BUY":
        target_price = round(entry_price + target_distance, 2)
    else:
        target_price = round(entry_price - target_distance, 2)

    reward_to_risk = round(target_distance / risk_per_share, 2)

    config = load_config()
    squareoff_time = config.get("squareoff_time", "15:15")

    plan = {
        "symbol": clean_symbol(symbol),
        "direction": direction,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_price, 2),
        "target_price": round(target_price, 2),
        "risk_per_share": risk_per_share,
        "target_gain_per_share": target_distance,
        "reward_to_risk": reward_to_risk,
        "cutoff_time_ist": f"{squareoff_time}:00 IST",
        "created_at_ist": now_ist().strftime("%Y-%m-%d %H:%M:%S IST"),
        "stop_rule": stop_mode,
        "target_rule": target_mode,
        "exchange": "NSE"
    }

    if write:
        os.makedirs(os.path.dirname(DEFAULT_PLAN_PATH), exist_ok=True)
        with open(DEFAULT_PLAN_PATH, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)

    return plan

def main():
    parser = argparse.ArgumentParser(description="Exit Planner for Indian Equities")
    parser.add_argument("--symbol", default="RELIANCE", help="NSE Symbol")
    parser.add_argument("--entry", type=float, default=1364.18, help="Entry price in INR")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--stop", default="or-mid", help="Stop mode: or-mid, or-low, or pts:<amount>")
    parser.add_argument("--target", default="1R", help="Target mode: 1R, 1.5R, 2R")
    parser.add_argument("--or-high", type=float, default=1359.20, help="Opening range high")
    parser.add_argument("--or-low", type=float, default=1347.00, help="Opening range low")
    parser.add_argument("--or-mid", type=float, default=1353.10, help="Opening range midpoint")
    parser.add_argument("--write", action="store_true", default=True, help="Write plan to trader/plan.json")

    args = parser.parse_args()

    plan = plan_exit(
        symbol=args.symbol,
        entry_price=args.entry,
        direction=args.direction,
        stop_mode=args.stop,
        target_mode=args.target,
        or_high=args.or_high,
        or_low=args.or_low,
        or_mid=args.or_mid,
        write=args.write
    )

    print("\n" + "=" * 76)
    print(f"TRADE EXIT PLAN: {plan['symbol']} ({plan['direction']})")
    print("=" * 76)
    print(f"Entry Price:           {format_inr(plan['entry_price'])}")
    print(f"Stop-Loss Price:       {format_inr(plan['stop_loss'])} ({plan['stop_rule']})")
    print(f"Risk per Share:        {format_inr(plan['risk_per_share'])}")
    print(f"Take-Profit Target:    {format_inr(plan['target_price'])} ({plan['target_rule']})")
    print(f"Target Gain per Share: {format_inr(plan['target_gain_per_share'])}")
    print(f"Reward-to-Risk:        {plan['reward_to_risk']}:1")
    print(f"Intraday Cutoff:       {plan['cutoff_time_ist']} (Mandatory Square-off)")
    print("=" * 76)
    if args.write:
        print(f"[OK] Trade plan saved to: {DEFAULT_PLAN_PATH}")
        print(">> Next step: Run '/trader-timemachine' to simulate 10,000 outcomes before risking money.")
    print("")

if __name__ == "__main__":
    main()
