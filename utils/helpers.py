import pandas as pd
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
        st.write("🔗 URL:", url)  # ✅ Show the full API request
        st.write("📄 Raw text (first 300 chars):", response.text[:300])  # ✅ Preview response

        if response.status_code != 200 or "timestamp" not in response.text:
            raise ValueError("Alpha Vantage API returned no time series data.")

        df = pd.read_csv(StringIO(response.text))
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp").sort_index()
        df = df.loc[start:end]
        df = df[["close"]].rename(columns={"close": "Close"})

        if df.empty:
            raise ValueError("No data returned in selected date range.")
        return df

    except Exception as e:
        st.error(f"Alpha Vantage error: {e}")
        raise ValueError("Failed to fetch price data. Check ticker symbols and date range.")
