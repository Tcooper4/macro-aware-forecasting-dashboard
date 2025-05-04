import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# === Load user strategy config ===
def load_config(path="config/config.json"):
    with open(path, "r") as f:
        return json.load(f)

# === Fetch historical price data ===
def fetch_price_data(ticker, start="2020-01-01", end=None):
    try:
        df = yf.download(ticker, start=start, end=end)
        if df.empty or "Close" not in df.columns:
            raise ValueError("No valid price data found.")
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"❌ Failed to fetch data for {ticker}: {e}")
        return pd.DataFrame()

# === Format price change as percentage string ===
def pct_format(val, digits=2):
    return f"{val*100:.{digits}f}%"

# === Normalize signal output for display ===
def format_signal_output(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:.4f}" if isinstance(x, (int, float, np.float64)) else x)
    return df
