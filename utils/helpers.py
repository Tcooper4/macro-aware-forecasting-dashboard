import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(tickers, start_date="2015-01-01", end_date=None, interval="1d"):
    """
    Fetch price data using yfinance with MultiIndex columns.
    Columns: ('Close', 'AAPL'), ('Volume', 'MSFT'), etc.
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    try:
        data = yf.download(
            tickers=tickers,
            start=start_date,
            end=end_date,
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            threads=True
        )
        # Ensure MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            return data
        else:
            # Convert single-ticker data to MultiIndex
            return pd.concat({tickers[0]: data}, axis=1)
    except Exception as e:
        print(f"❌ Failed to fetch data for {tickers}: {e}")
        return pd.DataFrame()

def preprocess_for_model(data, ticker, column='Close'):
    """
    Extracts a single column (e.g., 'Close') for a given ticker from MultiIndex DataFrame.
    Returns a clean series.
    """
    try:
        ts = data[(column, ticker)].dropna()
        ts.name = ticker
        return ts
    except KeyError:
        print(f"⚠️ Column ({column}, {ticker}) not found in data.")
        return pd.Series()

def scale_series(series):
    """Normalize series between 0 and 1."""
    return (series - series.min()) / (series.max() - series.min())

def unscale_series(scaled_series, original_series):
    """Restore original values from scaled series."""
    return scaled_series * (original_series.max() - original_series.min()) + original_series.min()

def aggregate_signals(signal_dict):
    """
    Given a dictionary of {model_name: signal}, return a final ensemble signal.
    Each signal should be in ['BUY', 'HOLD', 'SELL'].
    """
    from collections import Counter

    votes = list(signal_dict.values())
    vote_count = Counter(votes)

    # Voting logic
    if vote_count['BUY'] > vote_count['SELL']:
        return 'BUY'
    elif vote_count['SELL'] > vote_count['BUY']:
        return 'SELL'
    else:
        return 'HOLD'

def generate_signal_from_return(predicted_return, threshold=0.01):
    """
    Convert predicted return into trading signal.
    """
    if predicted_return > threshold:
        return 'BUY'
    elif predicted_return < -threshold:
        return 'SELL'
    else:
        return 'HOLD'

def train_test_split_series(series, test_size=0.2):
    """Split a time series into train and test sets."""
    split_idx = int(len(series) * (1 - test_size))
    return series[:split_idx], series[split_idx:]
