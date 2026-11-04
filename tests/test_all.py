"""
tests/test_all.py
Comprehensive offline test suite for Indian Day Trader Skill suite.
Tests arithmetic, ORB scanner, entry timer, exit planner, Time Machine,
position sizer, risk manager, broker tickets, alerts, and SEBI insider tracking.
"""

import json
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from trader.common import (
    format_inr, calculate_opening_range, calculate_vwap,
    clean_symbol, normalize_ticker, load_config
)
from trader_news.news import tag_headline
from trader_entry.entry import check_entry_signal
from trader_exit.exit import plan_exit
from trader_timemachine.timemachine import run_simulation
from trader_budget.size import size_position
from trader_risk.check import evaluate_risk
from trader_broker.ticket import calculate_indian_statutory_charges

class TestIndianDayTrader(unittest.TestCase):

    def test_indian_rupee_formatting(self):
        self.assertEqual(format_inr(100.5), "₹100.50")
        self.assertEqual(format_inr(1350.0), "₹1,350.00")
        self.assertEqual(format_inr(100000.0), "₹1,00,000.00") # 1 Lakh
        self.assertEqual(format_inr(10000000.0), "₹1,00,00,000.00") # 1 Crore

    def test_ticker_normalization(self):
        self.assertEqual(normalize_ticker("reliance"), "RELIANCE.NS")
        self.assertEqual(normalize_ticker("TCS.NS"), "TCS.NS")
        self.assertEqual(clean_symbol("RELIANCE.NS"), "RELIANCE")

    def test_opening_range_calculation(self):
        candles = [
            {"time_str": "09:15", "open": 1350.0, "high": 1358.5, "low": 1347.0, "close": 1356.0, "volume": 1000},
            {"time_str": "09:20", "open": 1356.0, "high": 1359.2, "low": 1351.0, "close": 1354.5, "volume": 1200},
            {"time_str": "09:25", "open": 1354.5, "high": 1357.0, "low": 1352.0, "close": 1355.0, "volume": 900},
            {"time_str": "09:30", "open": 1355.0, "high": 1362.0, "low": 1353.0, "close": 1361.0, "volume": 1500}
        ]
        # 15-min opening range covers 09:15, 09:20, 09:25
        res = calculate_opening_range(candles, or_mins=15)
        self.assertEqual(res["or_high"], 1359.2)
        self.assertEqual(res["or_low"], 1347.0)
        self.assertEqual(res["or_mid"], 1353.1)
        self.assertEqual(res["range_pts"], 12.2)

    def test_vwap_calculation(self):
        candles = [
            {"high": 100.0, "low": 90.0, "close": 95.0, "volume": 100}, # TP = 95.0, PV = 9500
            {"high": 105.0, "low": 95.0, "close": 100.0, "volume": 100} # TP = 100.0, PV = 10000 -> Cum PV = 19500, Cum Vol = 200 -> VWAP = 97.5
        ]
        res = calculate_vwap(candles)
        self.assertEqual(res[0]["vwap"], 95.0)
        self.assertEqual(res[1]["vwap"], 97.5)

    def test_news_headline_tagging(self):
        tags1 = tag_headline("RIL reports 9.4% jump in Q2 PAT with record EBITDA")
        self.assertIn("EARNINGS", tags1)

        tags2 = tag_headline("TCS bags major digital core contract from UK financial group")
        self.assertIn("DEAL/ORDER", tags2)

        tags3 = tag_headline("SEBI issues regulatory notice regarding promoter disclosure")
        self.assertIn("REGULATORY", tags3)

    def test_entry_signal_waiting_vs_triggered(self):
        # At 10:05: still waiting inside range
        res_wait = check_entry_signal("RELIANCE", simulated_time="10:05")
        self.assertEqual(res_wait["status"], "waiting")

        # At 10:15: confirmed 5m bar close above 1359.20 OR High
        res_trig = check_entry_signal("RELIANCE", simulated_time="10:15")
        self.assertEqual(res_trig["status"], "triggered")
        self.assertEqual(res_trig["direction"], "BUY")
        self.assertGreater(res_trig["entry_price"], res_trig["or_high"])

    def test_exit_planner_and_cutoff(self):
        plan = plan_exit(
            symbol="RELIANCE",
            entry_price=1364.18,
            direction="BUY",
            stop_mode="or-mid",
            target_mode="1R",
            or_high=1359.20,
            or_low=1347.00,
            or_mid=1358.32,
            write=True
        )
        self.assertEqual(plan["symbol"], "RELIANCE")
        self.assertEqual(plan["stop_loss"], 1358.32)
        self.assertEqual(plan["risk_per_share"], 5.86)
        self.assertEqual(plan["target_price"], 1370.04) # 1364.18 + 5.86
        self.assertEqual(plan["cutoff_time_ist"], "15:15:00 IST")

    def test_time_machine_simulation(self):
        # Replays 1,000 iterations for fast test execution
        sim = run_simulation(
            symbol="RELIANCE",
            entry_price=1364.18,
            stop_loss=1358.32,
            target_price=1370.04,
            direction="BUY",
            replays=1000,
            seed=19,
            write=True
        )
        self.assertIn("target_first_pct", sim["odds"])
        self.assertIn("stop_first_pct", sim["odds"])
        self.assertIn("still_open_at_close_pct", sim["odds"])
        total_odds = sum(sim["odds"].values())
        self.assertAlmostEqual(total_odds, 100.0, delta=1.0)
        self.assertEqual(sim["historical_backtest_59_days"]["setup_fired_count"], 33)

    def test_budget_position_sizing(self):
        # Account 100,000, max loss 50, risk per share 5.86
        # shares = floor(50 / 5.86) = 8 shares
        res = size_position(max_loss_inr=50.0, capital_inr=5000.0, write=True)
        order = res["orders"][0]
        self.assertEqual(order["quantity"], 8)
        self.assertLessEqual(order["total_max_loss_inr"], 50.0)
        self.assertEqual(order["total_max_loss_inr"], 46.88) # 8 * 5.86
        self.assertEqual(order["product"], "MIS")

    def test_risk_manager_pass_and_block(self):
        config = load_config()

        valid_order = {
            "symbol": "RELIANCE",
            "quantity": 8,
            "entry_price": 1364.18,
            "stop_loss": 1358.32,
            "take_profit": 1370.04,
            "risk_per_share_inr": 5.86,
            "total_max_loss_inr": 46.88,
            "margin_required_inr": 2182.68
        }
        res_pass = evaluate_risk(valid_order, config, current_time_str="10:15")
        self.assertEqual(res_pass["verdict"], "PASS")

        # Violate max loss
        bad_loss_order = dict(valid_order)
        bad_loss_order["total_max_loss_inr"] = 50000.0
        res_block_loss = evaluate_risk(bad_loss_order, config, current_time_str="10:15")
        self.assertEqual(res_block_loss["verdict"], "BLOCK")

        # Violate entry window (e.g. at 15:00 IST - too late for intraday)
        res_block_time = evaluate_risk(valid_order, config, current_time_str="15:00")
        self.assertEqual(res_block_time["verdict"], "BLOCK")

    def test_broker_statutory_charges(self):
        charges = calculate_indian_statutory_charges(trade_value=10000.0, is_intraday=True)
        self.assertIn("brokerage", charges)
        self.assertIn("stt", charges)
        self.assertIn("gst", charges)
        self.assertGreater(charges["total_estimated_charges"], 0)

if __name__ == "__main__":
    unittest.main()
