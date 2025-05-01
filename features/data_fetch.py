import wbdata
import pandas_datareader.data as web
import yfinance as yf
import pandas as pd
import datetime

# --- FRED data ---
def get_fred_series(series_code, start, end):
    return web.DataReader(series_code, "fred", start, end)

# --- World Bank data ---
def get_world_bank_series(indicator_code, countries, label, start, end):
    df = wbdata.get_dataframe({indicator_code: label}, country=countries).reset_index()
    df['date'] = pd.to_datetime(df['date'], format='%Y')
    if 'country' not in df.columns and len(countries) == 1:
        df['country'] = list(countries.keys())[0]
    return df[(df['date'] >= start) & (df['date'] <= end)]

# --- Stock price data ---
def get_yahoo_prices(tickers, start, end):
    df = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    return df.dropna()
