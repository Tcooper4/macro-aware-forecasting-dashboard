import yfinance as yf
import pandas as pd

def fetch_price_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    df = df[["Close"]]
    df.dropna(inplace=True)
    return df
