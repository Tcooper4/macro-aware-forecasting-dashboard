import pandas as pd
import yfinance as yf

def fetch_price_data(symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical price data using yfinance and clean it.
    """
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df.empty:
            print(f"⚠️ No data found for {symbol}")
            return None
        return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].dropna()
    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return None
