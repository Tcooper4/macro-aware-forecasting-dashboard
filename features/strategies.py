import pandas as pd

def generate_trade_signals(df: pd.DataFrame, strategy: str = "RSI Strategy") -> pd.Series:
    signal = pd.Series(index=df.index, dtype="object")

    if strategy == "RSI Strategy":
        signal[df["RSI"] < 30] = "BUY"
        signal[df["RSI"] > 70] = "SELL"
        signal[(df["RSI"] >= 30) & (df["RSI"] <= 70)] = "HOLD"

    elif strategy == "MACD Cross":
        cross_up = (df["MACD"] > df["MACD_Signal"]) & (df["MACD"].shift(1) <= df["MACD_Signal"].shift(1))
        cross_down = (df["MACD"] < df["MACD_Signal"]) & (df["MACD"].shift(1) >= df["MACD_Signal"].shift(1))
        signal[cross_up] = "BUY"
        signal[cross_down] = "SELL"
        signal[~(cross_up | cross_down)] = "HOLD"

    elif strategy == "EMA Crossover":
        cross_up = (df["EMA_Fast"] > df["EMA_Slow"]) & (df["EMA_Fast"].shift(1) <= df["EMA_Slow"].shift(1))
        cross_down = (df["EMA_Fast"] < df["EMA_Slow"]) & (df["EMA_Fast"].shift(1) >= df["EMA_Slow"].shift(1))
        signal[cross_up] = "BUY"
        signal[cross_down] = "SELL"
        signal[~(cross_up | cross_down)] = "HOLD"

    else:
        signal[:] = "HOLD"

    return signal.ffill()
