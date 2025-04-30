import pandas as pd

def calculate_indicators(df: pd.DataFrame, lookback: int = 14) -> pd.DataFrame:
    df = df.copy()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(lookback).mean()
    avg_loss = loss.rolling(lookback).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    df["EMA_Fast"] = df["Close"].ewm(span=8, adjust=False).mean()
    df["EMA_Slow"] = df["Close"].ewm(span=21, adjust=False).mean()

    return df
