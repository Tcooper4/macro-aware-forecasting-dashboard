import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")  # use your real key or set via Streamlit secrets

def fetch_price_data(ticker, start, end):
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={ticker}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}&datatype=csv"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Alpha Vantage request failed")

        text = response.text
        if "timestamp" not in text:
            raise ValueError("Alpha Vantage API returned no time series data (rate limited or invalid key?)")

        df = pd.read_csv(StringIO(text))
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
