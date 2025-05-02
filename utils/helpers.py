import pandas as pd
import numpy as np
import requests
import streamlit as st
from io import StringIO

ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "demo")

def fetch_price_data(ticker, start, end):
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={ticker}&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}&datatype=csv"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200 or "timestamp" not in response.text.lower():
            raise ValueError("Alpha Vantage returned no valid data")

        df = pd.read_csv(StringIO(response.text))
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp").sort_index()
        df = df.loc[start:end]
        df = df[["close"]].rename(columns={"close": "Close"})
        if df.empty:
            raise ValueError("No data in date range")
        return df

    except Exception as e:
        st.warning(f"Using fallback synthetic data for {ticker}: {e}")
        dates = pd.date_range(start=start, end=end)
        np.random.seed(len(ticker))
        synthetic = pd.Series(100 * np.cumprod(1 + np.random.normal(0.0005, 0.02, len(dates))), index=dates)
        return pd.DataFrame({"Close": synthetic})
