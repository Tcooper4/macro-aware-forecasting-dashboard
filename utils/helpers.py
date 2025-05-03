import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np

def fetch_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical adjusted close price data for a given ticker between start and end dates.
    """
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            return pd.DataFrame()
        df = df[['Adj Close']].rename(columns={'Adj Close': 'adj_close'})
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def calculate_returns(df: pd.DataFrame) -> pd.Series:
    """
    Calculate log returns from adjusted close prices.
    """
    return np.log(df['adj_close'] / df['adj_close'].shift(1)).dropna()

def generate_signal(forecast: pd.Series, actual: pd.Series) -> str:
    """
    Generate a trade signal based on forecast and actual price direction.
    """
    if forecast.iloc[-1] > actual.iloc[-1]:
        return "BUY"
    elif forecast.iloc[-1] < actual.iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

def aggregate_signals(results: list) -> pd.DataFrame:
    """
    Aggregate model results into a unified signal dataframe.
    """
    if not results:
        return pd.DataFrame(columns=["Ticker", "Signal", "Model", "Date", "Confidence"])

    df = pd.DataFrame(results)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df.sort_values(by=["Confidence"], ascending=False)

def normalize_series(series: pd.Series) -> pd.Series:
    """
    Normalize a time series between 0 and 1.
    """
    return (series - series.min()) / (series.max() - series.min())

def compute_moving_average(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    Compute simple moving average.
    """
    return df['adj_close'].rolling(window=window).mean()

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Compute Relative Strength Index (RSI) for a given price series.
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def safe_ticker_format(ticker: str) -> str:
    """
    Format ticker safely for use in file names or display.
    """
    return ticker.replace("/", "_").replace(".", "_")
