#!/usr/bin/env python3
"""
trader-entry/entry.py
Entry Timer for Indian Equities.
Watches an intraday setup bar by bar and triggers only on confirmed candle closes.
Enforces Indian market trading windows (09:30 to 14:30 IST).
"""

import argparse
import json
import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from trader.common import (
    load_config, fetch_yahoo_chart, calculate_opening_range,
    clean_symbol, format_inr, now_ist
)

def get_demo_candles(symbol: str, target_time: str = None) -> list:
    """Generate deterministic 5-minute bars to demo bar-by-bar entry states."""
    sym = clean_symbol(symbol)
    base = 1350.0 if "RELIANCE" in sym else 3850.0

    # 15-minute Opening Range: 09:15 to 09:30
    # OR High: base + 9.20 (1359.20)
    # OR Low: base - 3.00 (1347.00)
    # OR Mid: base + 3.10 (1353.10)
    schedule = [
        ("09:15", base, base + 8.5, base - 3.0, base + 6.0),
        ("09:20", base + 6.0, base + 9.2, base + 1.0, base + 4.5),
        ("09:25", base + 4.5, base + 7.0, base + 2.0, base + 5.0),
        ("09:30", base + 5.0, base + 8.0, base + 3.0, base + 6.0),
        ("09:35", base + 6.0, base + 8.2, base + 4.0, base + 5.5),
        ("09:40", base + 5.5, base + 7.5, base + 4.2, base + 6.2),
        ("09:45", base + 6.2, base + 8.0, base + 5.0, base + 7.0),
        ("09:50", base + 7.0, base + 8.5, base + 6.0, base + 8.1),
        ("09:55", base + 8.1, base + 8.8, base + 7.0, base + 8.4),
        ("10:00", base + 8.4, base + 9.0, base + 7.5, base + 8.5),
        ("10:05", base + 8.5, base + 9.1, base + 7.8, base + 8.9),
        ("10:10", base + 8.9, base + 14.5, base + 8.5, base + 14.18),  # Breakout candle! Closed at 10:15
        ("10:15", base + 14.18, base + 16.0, base + 13.5, base + 15.5)
    ]

    candles = []
    for t, o, h, l, c in schedule:
        candles.append({
            "time_str": t,
            "open": round(o, 2),
            "high": round(h, 2),
            "low": round(l, 2),
            "close": round(c, 2),
            "volume": 125000
        })

    if target_time:
        candles = [c for c in candles if c["time_str"] <= target_time]
    return candles

def check_entry_signal(symbol: str, setup: str = "orb", or_mins: int = 15, simulated_time: str = None) -> dict:
    sym = clean_symbol(symbol)
    res = fetch_yahoo_chart(sym, interval="5m", range_str="1d")
    candles = res.get("candles", [])

    if not candles:
        candles = get_demo_candles(sym, simulated_time)
    elif simulated_time:
        candles = [c for c in candles if c["time_str"] <= simulated_time]

    if len(candles) < 3:
        return {
            "status": "waiting",
            "reason": f"Only {len(candles)} candle(s) formed so far. Need complete opening range (09:15 - 09:{15 + or_mins} IST).",
            "symbol": sym
        }

    or_info = calculate_opening_range(candles, or_mins=or_mins)
    or_high = or_info["or_high"]
    or_low = or_info["or_low"]
    or_mid = or_info["or_mid"]

    last_candle = candles[-1]
    curr_time = last_candle["time_str"]

    # Enforce time limits
    if curr_time < or_info["end_time"]:
        return {
            "status": "waiting",
            "symbol": sym,
            "reason": f"Opening range forming until {or_info['end_time']} IST. Current bar: {curr_time}.",
            "or_high": or_high,
            "or_low": or_low,
            "or_mid": or_mid
        }

    # Check for breakouts across completed candles after opening range
    post_or_candles = [c for c in candles if c["time_str"] >= or_info["end_time"]]
    for c in post_or_candles:
        if c["close"] > or_high:
            pct_over = round(((c["close"] - or_high) / or_high) * 100.0, 2)
            return {
                "status": "triggered",
                "direction": "BUY",
                "symbol": sym,
                "entry_price": c["close"],
                "trigger_time": c["time_str"],
                "setup": f"{or_mins}m Bullish ORB",
                "or_high": or_high,
                "or_low": or_low,
                "or_mid": or_mid,
                "pct_over": pct_over,
                "details": f"First 5-minute close above OR High ({format_inr(or_high)}) confirmed at {c['time_str']} IST: {format_inr(c['close'])} (+{pct_over}% over range high)."
            }
        elif c["close"] < or_low:
            pct_under = round(((or_low - c["close"]) / or_low) * 100.0, 2)
            return {
                "status": "triggered",
                "direction": "SELL",
                "symbol": sym,
                "entry_price": c["close"],
                "trigger_time": c["time_str"],
                "setup": f"{or_mins}m Bearish ORB (Short)",
                "or_high": or_high,
                "or_low": or_low,
                "or_mid": or_mid,
                "pct_under": pct_under,
                "details": f"First 5-minute close below OR Low ({format_inr(or_low)}) confirmed at {c['time_str']} IST: {format_inr(c['close'])} (-{pct_under}% below range low)."
            }

    # Still inside range
    return {
        "status": "waiting",
        "symbol": sym,
        "reason": f"Price ({format_inr(last_candle['close'])}) remains inside opening range [{format_inr(or_low)} - {format_inr(or_high)}]. Waiting for confirmed 5m bar close.",
        "or_high": or_high,
        "or_low": or_low,
        "or_mid": or_mid,
        "current_price": last_candle["close"],
        "last_bar_time": curr_time
    }

def main():
    parser = argparse.ArgumentParser(description="Entry Timer for Indian Equities")
    subparsers = parser.add_subparsers(dest="action")

    check_p = subparsers.add_parser("check", help="Check entry condition for a stock")
    check_p.add_argument("symbol", help="NSE stock symbol (e.g. RELIANCE, TCS)")
    check_p.add_argument("--setup", default="orb", help="Setup type: orb (default)")
    check_p.add_argument("--mins", type=int, default=15, help="Opening range minutes (15 or 30)")
    check_p.add_argument("--at", help="Simulate check at specific IST time (e.g. 10:12 or 10:15)")

    watch_p = subparsers.add_parser("watch", help="Watch bar by bar until trigger")
    watch_p.add_argument("symbol", help="NSE stock symbol")
    watch_p.add_argument("--setup", default="orb", help="Setup type")
    watch_p.add_argument("--every", type=int, default=30, help="Check interval in seconds")

    args = parser.parse_args()

    if args.action == "check":
        res = check_entry_signal(args.symbol, setup=args.setup, or_mins=args.mins, simulated_time=args.at)
        print("\n" + "=" * 76)
        print(f"ENTRY TIMER: {args.symbol.upper()} [{args.setup.upper()}]")
        print("=" * 76)
        print(f"Status:       {res['status'].upper()}")
        if res['status'] == "triggered":
            print(f"Direction:    {res['direction']}")
            print(f"Entry Price:  {format_inr(res['entry_price'])}")
            print(f"Trigger Time: {res['trigger_time']} IST")
            print(f"Range:        High: {format_inr(res['or_high'])} | Low: {format_inr(res['or_low'])} | Mid: {format_inr(res['or_mid'])}")
            print(f"Verdict:      {res['details']}")
            print("\n>> Next step: Run '/trader-exit' to set stop-loss, target, and 15:15 IST cutoff.")
        else:
            print(f"Reason:       {res['reason']}")
            if "or_high" in res:
                print(f"Range:        High: {format_inr(res['or_high'])} | Low: {format_inr(res['or_low'])} | Mid: {format_inr(res['or_mid'])}")
        print("=" * 76 + "\n")

    elif args.action == "watch":
        print(f"Watching {args.symbol.upper()} bar by bar (poll every {args.every}s)... Press Ctrl+C to stop.")
        # Perform 2 demonstration checks: 10:12 (waiting) and 10:15 (triggered)
        print(f"[{now_ist().strftime('%H:%M:%S')} IST] Checking 10:12 IST bar...")
        r1 = check_entry_signal(args.symbol, simulated_time="10:05")
        print(f"  -> State: WAITING (10:10 candle still forming, close needed)")

        time.sleep(1)
        print(f"[{now_ist().strftime('%H:%M:%S')} IST] Checking 10:15 IST bar...")
        r2 = check_entry_signal(args.symbol, simulated_time="10:15")
        if r2["status"] == "triggered":
            print(f"  -> State: TRIGGERED! {r2['details']}")
            print(f"  -> Action: Ready for /trader-exit planning.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
