import pandas as pd
import numpy as np
import os
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime


def fetch_price_data(ticker: str, start_date: str = "2020-01-01", end_date: str = None) -> pd.Series:
    """
    Fetch historical closing prices for a single ticker using yfinance-style MultiIndex.
    Returns the Close price series (not Adj Close).
    """
    import yfinance as yf
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')

    df = yf.download(ticker, start=start_date, end=end_date, group_by="ticker", progress=False)

    # yfinance returns MultiIndex columns if group_by="ticker" and multiple tickers requested
    # For a single ticker, try to pull ('Close', ticker) or fallback to 'Close'
    try:
        if isinstance(df.columns, pd.MultiIndex):
            return df[('Close', ticker)].dropna()
        else:
            return df['Close'].dropna()
    except KeyError:
        raise KeyError(f"Close price not found in yfinance data for {ticker}")


def generate_forecast_signal(prices: pd.Series, forecast_horizon: int = 5) -> str:
    """
    Fit an ARIMA model and generate a BUY, HOLD, or SELL signal.
    """
    if len(prices) < 30:
        return "HOLD"  # Not enough data

    try:
        model = ARIMA(prices, order=(5, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=forecast_horizon)
        future_return = (forecast[-1] - prices.iloc[-1]) / prices.iloc[-1]

        if future_return > 0.02:
            return "BUY"
        elif future_return < -0.02:
            return "SELL"
        else:
            return "HOLD"
    except Exception as e:
        print(f"ARIMA failed for ticker: {e}")
        return "HOLD"


def save_trade_results(trade_data: pd.DataFrame, file_path: str = "data/top_trades.csv"):
    """
    Save trade signals to a CSV file. If empty, create file with headers only.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if trade_data.empty:
        headers = ["Ticker", "Date", "Forecast", "Signal"]
        pd.DataFrame(columns=headers).to_csv(file_path, index=False)
    else:
        trade_data.to_csv(file_path, index=False)


def aggregate_signals(tickers: list[str]) -> pd.DataFrame:
    """
    Loop through all tickers, fetch price data, forecast signal, and return trade ideas.
    """
    results = []
    for ticker in tickers:
        try:
            prices = fetch_price_data(ticker)
            signal = generate_forecast_signal(prices)
            results.append({
                "Ticker": ticker,
                "Date": datetime.today().strftime("%Y-%m-%d"),
                "Forecast": round(((prices[-1] - prices[-5]) / prices[-5]) * 100, 2) if len(prices) >= 5 else 0.0,
                "Signal": signal
            })
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            continue

    return pd.DataFrame(results)
