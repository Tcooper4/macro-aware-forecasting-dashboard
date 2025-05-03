import os
import pandas as pd
import requests
from datetime import datetime

def fetch_price_data(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Alpha Vantage API key not found in environment.")

    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact",
        "datatype": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Invalid response for {symbol}: {data}")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index", dtype=float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. adjusted close": "Adj Close",
        "6. volume": "Volume"
    }, inplace=True)

    return df
