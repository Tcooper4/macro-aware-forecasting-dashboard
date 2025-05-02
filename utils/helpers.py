import pandas as pd
import numpy as np
import requests
import streamlit as st
from io import StringIO

ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "demo")

def fetch_price_data(ticker, start, end):
    """
    Fetches daily close price data from Alpha Vantage.
    Falls back to realistic synthetic data if request fails.
    """
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={ticker}&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}&datatype=csv"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Alpha Vantage response not OK")

        # Check for valid CSV format with 'timestamp' column
        if "timestamp" not in response.text.lower():
            raise ValueError("Alpha Vantage API returned no time series data")

        df = pd.read_csv(StringIO(response.text))
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp").sort_index()
        df = df.loc[start:end]

        if "close" not in df.columns:
            raise ValueError("Missing 'close' column in Alpha Vantage data")

        df = df[["close"]].rename(columns={"close": "Close"})
        if df.empty:
            raise ValueError("No valid data in selected date range")

        return df

    except Exception as e:
        st.warning(f"Using fallback synthetic data for {ticker}: {e}")
        dates = pd.date_range(start=start, end=end)
        np.random.seed(len(ticker))  # deterministic per ticker
        returns = np.random.normal(loc=0.0005, scale=0.02, size=len(dates))  # realistic daily returns
        prices = 100 * np.cumprod(1 + returns)
        return pd.DataFrame({"Close": prices}, index=dates)
