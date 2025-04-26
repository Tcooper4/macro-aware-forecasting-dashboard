# src/features/merge_data.py

import pandas as pd
import yfinance as yf

def merge_data(ticker: str) -> pd.DataFrame:
    """
    Fetch real historical stock close prices from Yahoo Finance.
    """
    data = yf.download(ticker, start="2020-01-01", end="2025-01-01")
    data = data.rename(columns={"Close": f"{ticker}_Close"})
    return data
