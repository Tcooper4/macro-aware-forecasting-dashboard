import pandas as pd
import yfinance as yf
import traceback

def merge_data(ticker: str) -> pd.DataFrame:
    """
    Fetch historical adjusted close prices from Yahoo Finance.

    Parameters:
    ----------
    ticker : str
        Stock ticker symbol (e.g., "AAPL").

    Returns:
    -------
    pd.DataFrame
        DataFrame containing the renamed adjusted close price series with a datetime index.
    """
    try:
        data = yf.download(ticker, start="2020-01-01", end="2025-01-01", progress=False, auto_adjust=True)
        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")
        data = data.rename(columns={"Close": f"{ticker}_Close"})
        return data[[f"{ticker}_Close"]]
    except Exception as e:
        traceback.print_exc()  # print full stack trace in terminal or Streamlit log
        raise RuntimeError(f"Failed to fetch or process data for {ticker}: {e}")
