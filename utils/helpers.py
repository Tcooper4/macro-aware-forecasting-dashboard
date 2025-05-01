import yfinance as yf
import pandas as pd

def fetch_price_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    if df.empty or "Close" not in df.columns:
        raise ValueError(f"No valid data returned for ticker '{ticker}'")
    df = df[["Close"]].dropna()
    return df
