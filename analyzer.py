import yfinance as yf
import pandas as pd

from config import *

def analyze_stock(symbol):

    data = yf.Ticker(symbol).history(period=LOOKBACK_PERIOD)

    if data.empty or len(data) < 60:
        return None

    close = data["Close"]
    volume = data["Volume"]

    price = close.iloc[-1]

    if price < MIN_PRICE:
        return None

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.iloc[-1]

    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    macd_val = macd.iloc[-1]
    signal_val = signal.iloc[-1]

    avg_vol = volume.rolling(20).mean().iloc[-1]
    rvol = volume.iloc[-1] / avg_vol if avg_vol != 0 else 0

    score = 0

    # 🔥 نظام نقاط محسّن
    if price > ma50:
        score += 30

    if ma20 > ma50:
        score += 20

    if 45 <= rsi <= 70:
        score += 20

    if macd_val > signal_val:
        score += 20

    if rvol > 1.5:
        score += 10

    # 🧠 القرار
    if score >= 80:
        decision = "STRONG BUY"
    elif score >= 60:
        decision = "WATCHLIST"
    else:
        decision = "AVOID"

    return {
        "Symbol": symbol,
        "Price": round(price, 2),
        "Score": int(score),
        "RSI": round(rsi, 1),
        "MACD": round(macd_val, 3),
        "RVOL": round(rvol, 2),
        "Decision": decision
    }