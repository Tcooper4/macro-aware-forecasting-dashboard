import os
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf

def fetch_price_data(ticker, period="6mo", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)

        if data.empty:
            print(f"⚠️ No data returned for {ticker}")
            return None

        # Reset index and ensure expected structure
        data = data.reset_index()

        # Ensure 'Close' column is present and valid
        if 'Close' not in data.columns:
            print(f"❌ 'Close' column missing in data for {ticker}")
            return None

        # Convert Close to numeric (coerce invalids to NaN)
        data["Close"] = pd.to_numeric(data["Close"], errors="coerce")

        # Drop rows where Close is NaN
        data = data.dropna(subset=["Close"])
        if data.empty:
            print(f"❌ All 'Close' values are NaN for {ticker}")
            return None

        return data

    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return None

