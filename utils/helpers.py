import os
import pandas as pd
import yfinance as yf
from datetime import datetime

def fetch_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical adjusted close price data for a given ticker.
    Logs debug info for each download attempt and handles both MultiIndex and flat structures.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "debug_fetch_price_data.log")

    def log_debug(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {ticker}: {message}\n")

    try:
        df = yf.download(ticker, start=start_date, end=end_date, group_by="ticker")
        log_debug(f"Downloaded columns: {df.columns.tolist()}")
        log_debug(f"First 5 rows:\n{df.head().to_string()}")

        if df.empty:
            msg = "⚠️ No data returned"
            print(f"{msg} for {ticker}")
            log_debug(msg)
            return pd.DataFrame()

        # Handle MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            if (ticker, 'Adj Close') in df.columns:
                series = df[(ticker, 'Adj Close')].rename("adj_close")
            elif (ticker, 'Close') in df.columns:
                msg = "⚠️ Using 'Close' instead of 'Adj Close'"
                print(f"{msg} for {ticker}")
                log_debug(msg)
                series = df[(ticker, 'Close')].rename("adj_close")
            else:
                msg = "❌ Neither 'Adj Close' nor 'Close' in MultiIndex columns"
                print(f"{msg} for {ticker}")
                log_debug(msg)
                return pd.DataFrame()
        else:
            if 'Adj Close' in df.columns:
                series = df['Adj Close'].rename("adj_close")
            elif 'Close' in df.columns:
                msg = "⚠️ Using 'Close' instead of 'Adj Close'"
                print(f"{msg} for {ticker}")
                log_debug(msg)
                series = df['Close'].rename("adj_close")
            else:
                msg = "❌ Neither 'Adj Close' nor 'Close' in flat columns"
                print(f"{msg} for {ticker}")
                log_debug(msg)
                return pd.DataFrame()

        return pd.DataFrame(series).dropna()

    except Exception as e:
        msg = f"❌ Exception: {e}"
        print(f"{msg} for {ticker}")
        log_debug(msg)
        return pd.DataFrame()
