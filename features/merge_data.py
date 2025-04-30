import yfinance as yf
import pandas as pd
import numpy as np
import traceback

# Dummy macro fetcher (replace with your real macro fetcher)
def fetch_macro_data():
    try:
        # Simulate macro data (e.g. interest rate, inflation, etc.)
        dates = pd.date_range(start="2015-01-01", end=pd.Timestamp.today(), freq='M')
        data = {
            "Interest_Rate": np.random.uniform(0.5, 5.0, len(dates)),
            "Inflation": np.random.uniform(1.0, 3.5, len(dates)),
        }
        macro_df = pd.DataFrame(data, index=dates)
        macro_df.index.name = "Date"
        return macro_df
    except Exception as e:
        print("Macro data fetch failed:", e)
        return pd.DataFrame()

def merge_data(ticker):
    try:
        print(f"📡 Fetching data for ticker: {ticker}")
        price_data = yf.download(ticker, start="2015-01-01", end=pd.Timestamp.today(), auto_adjust=True)

        if price_data is None or price_data.empty:
            raise ValueError("No price data retrieved.")

        price_data = price_data[['Close']].rename(columns={"Close": f"{ticker}_Close"})
        price_data.index.name = "Date"

        print("✅ Price data fetched")

        macro_data = fetch_macro_data()
        if macro_data.empty:
            print("⚠️ Warning: Macro data is empty. Proceeding with price data only.")
            merged = price_data
        else:
            merged = pd.merge(price_data, macro_data, how='left', left_index=True, right_index=True)

        merged.ffill(inplace=True)
        merged.dropna(inplace=True)

        if merged.empty:
            raise ValueError("Merged dataset is empty after cleaning.")

        print(f"✅ Merged data shape: {merged.shape}")
        return merged

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Failed to fetch or process data for {ticker}: {e}")
