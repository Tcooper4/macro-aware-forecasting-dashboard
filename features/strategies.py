import pandas as pd

def rsi_strategy(df, lookback=14):
    df = df.copy()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(lookback).mean()
    avg_loss = loss.rolling(lookback).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    df["Signal"] = "HOLD"
    df.loc[df["RSI"] < 30, "Signal"] = "BUY"
    df.loc[df["RSI"] > 70, "Signal"] = "SELL"
    return df[["Close", "RSI", "Signal"]]

def macd_strategy(df):
    df = df.copy()
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Signal"] = "HOLD"
    df.loc[
        (df["MACD"] > df["MACD_Signal"]) & 
        (df["MACD"].shift(1) <= df["MACD_Signal"].shift(1)), "Signal"
    ] = "BUY"
    df.loc[
        (df["MACD"] < df["MACD_Signal"]) & 
        (df["MACD"].shift(1) >= df["MACD_Signal"].shift(1)), "Signal"
    ] = "SELL"
    return df[["Close", "MACD", "MACD_Signal", "Signal"]]

def ema_crossover_strategy(df, fast=8, slow=21):
    df = df.copy()
    df["EMA_Fast"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df["EMA_Slow"] = df["Close"].ewm(span=slow, adjust=False).mean()
    df["Signal"] = "HOLD"
    df.loc[
        (df["EMA_Fast"] > df["EMA_Slow"]) & 
        (df["EMA_Fast"].shift(1) <= df["EMA_Slow"].shift(1)), "Signal"
    ] = "BUY"
    df.loc[
        (df["EMA_Fast"] < df["EMA_Slow"]) & 
        (df["EMA_Fast"].shift(1) >= df["EMA_Slow"].shift(1)), "Signal"
    ] = "SELL"
    return df[["Close", "EMA_Fast", "EMA_Slow", "Signal"]]
