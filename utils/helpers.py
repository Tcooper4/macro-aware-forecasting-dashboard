import os
import pandas as pd
import requests
from datetime import datetime

def fetch_price_data(symbol, start="2020-01-01", end=None):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Alpha Vantage API key not found in environment.")

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}"
    r = requests.get(url)
    data = r.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Alpha Vantage error: {data.get('Note') or data.get('Error Message') or 'Invalid response'}")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df = df.rename(columns={"5. adjusted close": "Close"})
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df["Close"] = df["Close"].astype(float)

    if end:
        df = df[(df.index >= start) & (df.index <= end)]
    else:
        df = df[df.index >= start]

    return df
