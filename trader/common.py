"""
Shared utilities for Indian Day Trader Skill suite.
Handles Indian Standard Time (IST), Yahoo Finance (.NS) data fetching,
order/plan file persistence, and financial arithmetic.
"""

import json
import math
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# IST is UTC + 5:30
IST_OFFSET = timedelta(hours=5, minutes=30)
IST_TZ = timezone(IST_OFFSET, name="IST")

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_UNIVERSE_PATH = os.path.join(os.path.dirname(__file__), "universe.json")
DEFAULT_PLAN_PATH = os.path.join(os.path.dirname(__file__), "plan.json")
DEFAULT_ORDERS_PATH = os.path.join(os.path.dirname(__file__), "orders.json")
DEFAULT_ALERTS_PATH = os.path.join(os.path.dirname(__file__), "alerts.json")
DEFAULT_TIMEMACHINE_PATH = os.path.join(os.path.dirname(__file__), "timemachine.json")
DEFAULT_PAPER_PATH = os.path.join(os.path.dirname(__file__), "paper_trades.json")

def now_ist() -> datetime:
    """Return current datetime in Indian Standard Time (IST)."""
    return datetime.now(timezone.utc).astimezone(IST_TZ)

def format_inr(amount: float) -> str:
    """Format floating point numbers into Indian Rupee format (₹ xx,xx,xxx.xx)."""
    if math.isnan(amount) or math.isinf(amount):
        return "₹ 0.00"
    is_negative = amount < 0
    abs_amt = abs(amount)
    parts = f"{abs_amt:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last3 = integer_part[-3:]
        rest = integer_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted = ",".join(groups) + "," + last3

    sign = "-" if is_negative else ""
    return f"{sign}₹{formatted}.{decimal_part}"

def load_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback default configuration
    return {
        "account_capital_inr": 100000.0,
        "max_loss_per_trade_inr": 1000.0,
        "max_daily_loss_inr": 3000.0,
        "max_trades_per_day": 3,
        "min_reward_to_risk": 1.5,
        "entry_start_time": "09:30",
        "entry_cutoff_time": "14:30",
        "squareoff_time": "15:15",
        "market_close_time": "15:30",
        "paper": True,
        "broker": "zerodha",
        "mis_leverage_multiplier": 5.0,
        "exchange": "NSE",
        "user_agent": "IndianDayTrader/2.0 (NSE-BSE Public Research, contact: trader@example.com)"
    }

def load_universe(path: str = DEFAULT_UNIVERSE_PATH) -> list:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {"symbol": "RELIANCE", "ticker": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy & Retail"},
        {"symbol": "TCS", "ticker": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT"},
        {"symbol": "HDFCBANK", "ticker": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
        {"symbol": "INFY", "ticker": "INFY.NS", "name": "Infosys", "sector": "IT"},
        {"symbol": "ICICIBANK", "ticker": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"}
    ]

def normalize_ticker(symbol: str) -> str:
    """Normalize input like 'RELIANCE' or 'reliance' or 'RELIANCE.NS' into 'RELIANCE.NS'."""
    clean = symbol.strip().upper()
    if clean.endswith(".NS") or clean.endswith(".BO"):
        return clean
    return f"{clean}.NS"

def clean_symbol(ticker: str) -> str:
    """Get raw NSE symbol without .NS or .BO suffix."""
    return ticker.split(".")[0].upper()

def fetch_yahoo_chart(ticker: str, interval: str = "5m", range_str: str = "1d", user_agent: str = None) -> dict:
    """
    Fetch intraday or historical candle data from Yahoo Finance chart API.
    Returns normalized list of candles:
    [{'timestamp': int, 'dt_ist': str, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': int}]
    """
    full_ticker = normalize_ticker(ticker)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{full_ticker}?interval={interval}&range={range_str}"
    ua = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    req = urllib.request.Request(url, headers={"User-Agent": ua})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data.get("chart", {}).get("result")
            if not result:
                return {"error": f"No data returned for {full_ticker}", "candles": []}

            quote_data = result[0]
            meta = quote_data.get("meta", {})
            timestamps = quote_data.get("timestamp", [])
            indicators = quote_data.get("indicators", {}).get("quote", [{}])[0]
            opens = indicators.get("open", [])
            highs = indicators.get("high", [])
            lows = indicators.get("low", [])
            closes = indicators.get("close", [])
            volumes = indicators.get("volume", [])

            candles = []
            for i, ts in enumerate(timestamps):
                if (i < len(opens) and opens[i] is not None and
                    i < len(highs) and highs[i] is not None and
                    i < len(lows) and lows[i] is not None and
                    i < len(closes) and closes[i] is not None):

                    dt_ist = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(IST_TZ)
                    candles.append({
                        "timestamp": ts,
                        "dt_ist": dt_ist.strftime("%Y-%m-%d %H:%M:%S"),
                        "time_str": dt_ist.strftime("%H:%M"),
                        "open": round(float(opens[i]), 2),
                        "high": round(float(highs[i]), 2),
                        "low": round(float(lows[i]), 2),
                        "close": round(float(closes[i]), 2),
                        "volume": int(volumes[i]) if (i < len(volumes) and volumes[i] is not None) else 0
                    })

            return {
                "symbol": clean_symbol(full_ticker),
                "ticker": full_ticker,
                "currency": meta.get("currency", "INR"),
                "regularMarketPrice": meta.get("regularMarketPrice", 0.0),
                "previousClose": meta.get("chartPreviousClose", 0.0),
                "candles": candles
            }
    except Exception as e:
        return {"error": str(e), "candles": []}

def calculate_vwap(candles: list) -> list:
    """Calculate cumulative Volume Weighted Average Price (VWAP) for candles."""
    cum_vol = 0
    cum_pv = 0.0
    res = []
    for c in candles:
        typical_price = (c["high"] + c["low"] + c["close"]) / 3.0
        vol = c.get("volume", 0)
        cum_vol += vol
        cum_pv += typical_price * vol
        vwap = round(cum_pv / cum_vol, 2) if cum_vol > 0 else typical_price
        c_copy = dict(c)
        c_copy["vwap"] = vwap
        res.append(c_copy)
    return res

def calculate_opening_range(candles: list, or_mins: int = 15) -> dict:
    """
    Calculate opening range (09:15 AM to 09:15 + or_mins IST).
    For 15-min ORB: 09:15 - 09:30.
    For 30-min ORB: 09:15 - 09:45.
    """
    end_time_str = "09:30" if or_mins == 15 else "09:45"
    or_candles = [c for c in candles if "09:15" <= c["time_str"] < end_time_str]

    if not or_candles:
        # Fallback to first candle if session just started
        if candles:
            or_candles = [candles[0]]
        else:
            return {"or_high": 0.0, "or_low": 0.0, "or_mid": 0.0, "candles_count": 0}

    or_high = max(c["high"] for c in or_candles)
    or_low = min(c["low"] for c in or_candles)
    or_mid = round((or_high + or_low) / 2.0, 2)

    return {
        "or_high": round(or_high, 2),
        "or_low": round(or_low, 2),
        "or_mid": or_mid,
        "range_pts": round(or_high - or_low, 2),
        "candles_count": len(or_candles),
        "end_time": end_time_str
    }
