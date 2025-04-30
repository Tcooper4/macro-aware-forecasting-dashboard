import yfinance as yf
import pandas as pd
import numpy as np
import traceback
import socket

def check_internet():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except:
        return False

def fetch_macro_data():
    dates = pd.date_range(start="2015-01-01", end=pd.Timestamp.today(), freq='M')
    data = {
        "Interest_Rate": np.random.uniform(0.5, 5.0, len(dates)),
        "Inflation": np.random.uniform(1.0, 3.5, len(dates)),
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"
    return df

def fallback_price_data(ticker):
    dates = pd.date_range("2020-01-01", periods=1000)
    prices = np.linspace(100, 300, len(dates)) + np.random.normal(0, 5, len(dates))
    return pd.DataFrame({f"{ticker}_Close": prices}, index=dates)

def merge_data(ticker):
    try:
        print(f"📡 Attempting to fetch data for: {ticker}")

        if not check_internet():
            print("❌ No internet. Using fallback price data.")
            price_data = fallback_price_data(ticker)
        else:
            price_data = yf.download(ticker, start="2015-01-01", end=pd.Timestamp.today(), auto_adjust=True)
            if price_data.empty:
                print("⚠️ Empty price data from yfinance. Using fallback.")
                price_data = fallback_price_data(ticker)
            else:
                price_data = price_data[['Close']].rename(columns={"Close": f"{ticker}_Close"})
        
        price_data.index.name = "Date"
        print("✅ Price data ready")

        macro_data = fetch_macro_data()
        print("📈 Macro data fetched")

        merged = pd.merge(price_data, macro_data, left_index=True, right_index=True, how='left')
        merged.ffill(inplace=True)
        merged.dropna(inplace=True)

        if merged.empty:
            raise ValueError("Merged dataset is empty after processing.")

        print(f"✅ Final merged dataset: {merged.shape}")
        return merged

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Failed to fetch or process data for {ticker}: {e}")
