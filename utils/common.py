import yfinance as yf
import pandas as pd

def fetch_price_data(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            raise ValueError(f"No data returned for {ticker}")
        return df
    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def preprocess_for_model(df):
    df = df.copy()
    df.dropna(inplace=True)
    if "Close" not in df.columns:
        raise ValueError("Missing 'Close' column in price data")
    return df

def generate_signal_from_return(ret, thresholds):
    if ret is None:
        return "HOLD"
    if ret >= thresholds.get("buy", 5.0):
        return "BUY"
    elif ret <= thresholds.get("sell", -5.0):
        return "SELL"
    else:
        return "HOLD"
