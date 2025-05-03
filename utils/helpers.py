import os
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf

def fetch_price_data(symbol, period="6mo", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
        df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
        df.dropna(inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {symbol}: {e}")
