import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(ticker, start_date=None, end_date=None):
    """
    Fetches historical adjusted close price data for a given ticker.
    Uses 'Close' as the adjusted close when auto_adjust=True.
    """
    if not start_date:
        start_date = datetime.today() - timedelta(days=365 * 5)
    if not end_date:
        end_date = datetime.today()

    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

    # Check if data exists
    if df.empty or "Close" not in df.columns:
        raise ValueError(f"No valid data returned for {ticker}")

    df = df[["Close"]].dropna()
    df.columns = ["Close"]
    return df
