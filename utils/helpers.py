import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO  # ✅ fix: use built-in module

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")  # replace "demo" if using Streamlit secrets

def fetch_price_data(ticker, start, end):
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={ticker}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}&datatype=csv"
    )
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Alpha Vantage request failed")

        df = pd.read_csv(StringIO(response.text))  # ✅ fixed here
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
        df = df.sort_index()
        df = df.loc[start:end]
        df = df[["adjusted_close"]].rename(columns={"adjusted_close": "Close"})

        if df.empty:
            raise ValueError("No data returned in date range")

        return df

    except Exception as e:
        raise ValueError(f"Alpha Vantage error: {e}")
