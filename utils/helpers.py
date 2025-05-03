import yfinance as yf

def fetch_price_data(symbol, start="2015-01-01", end=None):
    try:
        symbol = str(symbol).strip()  # Ensure it's a clean string
        data = yf.download(tickers=[symbol], start=start, end=end)
        if data.empty:
            return None
        return data
    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return None
