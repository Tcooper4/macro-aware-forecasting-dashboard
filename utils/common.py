import yfinance as yf

def fetch_price_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        raise ValueError(f"No data found for {ticker}")
    return data

def preprocess_for_model(data, ticker, column='Close'):
    if column not in data.columns:
        raise ValueError(f"{column} not found in data for {ticker}")
    return data[column].dropna()

def generate_signal_from_return(return_val, buy_threshold=0.05, sell_threshold=-0.05):
    if return_val > buy_threshold:
        return 'BUY'
    elif return_val < sell_threshold:
        return 'SELL'
    else:
        return 'HOLD'
