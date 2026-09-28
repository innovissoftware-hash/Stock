import pandas as pd
import numpy as np
import yfinance as yf

def fetch_daily(ticker: str, period="5y"):
    ticker = ticker.upper().strip()
    df = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True, repair=True)
    if df.empty:
        raise ValueError(f"No data found for {ticker}")
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    for n in (50, 100, 200):
        df[f"SMA{n}"] = df["Close"].rolling(n).mean()
    df["Volume20"] = df["Volume"].rolling(20).mean()
    df["RSI14"] = rsi(df["Close"], 14)
    df["MACD"], df["MACDSignal"] = macd(df["Close"])
    return df.dropna(subset=["SMA200"])

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    line = ema_fast - ema_slow
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig

def resample_ohlcv(df, rule):
    out = df[["Open","High","Low","Close","Volume"]].resample(rule).agg({
        "Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"
    }).dropna()
    return out

def candle_pattern(row):
    o,h,l,c = row[["Open","High","Low","Close"]]
    body = abs(c-o)
    rng = max(h-l, 1e-9)
    upper = h-max(o,c)
    lower = min(o,c)-l

    if body/rng < 0.10:
        return "Doji / indecision"
    if lower > body*2 and upper < body:
        return "Hammer-like"
    if upper > body*2 and lower < body:
        return "Shooting-star-like"
    if c > o:
        return "Bullish candle"
    return "Bearish candle"

def timeframe_summary(df, rule):
    x = resample_ohlcv(df, rule)
    x["SMA20"] = x["Close"].rolling(20).mean()
    x["SMA50"] = x["Close"].rolling(50).mean()
    if len(x) < 10:
        return {"trend":"Insufficient data","pattern":"N/A","last_close":None}
    recent = x.tail(6)
    slope = recent["Close"].iloc[-1] - recent["Close"].iloc[0]
    trend = "Rising" if slope > 0 else "Falling" if slope < 0 else "Flat"
    return {
        "trend": trend,
        "pattern": candle_pattern(x.iloc[-1]),
        "last_close": float(x["Close"].iloc[-1]),
        "bars": x
    }

def analyze(ticker):
    d = fetch_daily(ticker)
    last = d.iloc[-1]
    price = float(last["Close"])

    levels = {n: float(last[f"SMA{n}"]) for n in (50,100,200)}
    above = {n: price > levels[n] for n in levels}

    dma_alignment = (
        "Positive" if levels[50] > levels[100] > levels[200]
        else "Negative" if levels[50] < levels[100] < levels[200]
        else "Mixed"
    )

    score = 0
    score += 1 if above[50] else -1
    score += 1 if above[100] else -1
    score += 1 if above[200] else -1
    score += 1 if levels[50] > levels[100] else -1
    score += 1 if levels[100] > levels[200] else -1
    score += 1 if last["RSI14"] >= 50 else -1
    score += 1 if last["MACD"] > last["MACDSignal"] else -1

    bias = "Bullish technical bias" if score >= 4 else "Bearish technical bias" if score <= -4 else "Neutral/mixed technical bias"

    weekly = timeframe_summary(d, "W-FRI")
    monthly = timeframe_summary(d, "ME")

    return {
        "ticker": ticker.upper(),
        "data": d,
        "price": price,
        "dma": levels,
        "above_dma": above,
        "alignment": dma_alignment,
        "score": score,
        "bias": bias,
        "rsi": float(last["RSI14"]),
        "macd": float(last["MACD"]),
        "macd_signal": float(last["MACDSignal"]),
        "volume_ratio": float(last["Volume"] / last["Volume20"]) if last["Volume20"] else None,
        "weekly": weekly,
        "monthly": monthly,
        "as_of": d.index[-1]
    }
