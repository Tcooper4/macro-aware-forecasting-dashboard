import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(ticker, start_date=None, end_date=None):
    if not start_date:
        start_date = datetime.today() - timedelta(days=365 * 5)
    if not end_date:
        end_date = datetime.today()

    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

    # Ensure there is a Close column
    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        else:
            raise ValueError(f"'Close' column missing in data for {ticker}")

    df = df[['Close']].dropna()
    df.columns = ['Close']
    return df
