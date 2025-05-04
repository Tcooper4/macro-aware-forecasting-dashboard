import pandas as pd
import numpy as np
import os
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime


def fetch_price_data(ticker, start_date="2020-01-01", end_date=None):
    import yfinance as yf
    import pandas as pd

    if end_date is None:
        end_date = pd.to_datetime("today").strftime("%Y-%m-%d")

    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

    if df.empty or "Close" not in df.columns:
        raise ValueError(f"Close price not found in yfinance data for {ticker}")

    return df["Close"]



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
        future_return = (forecast.iloc[-1] - prices.iloc[-1]) / prices.iloc[-1]

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
            forecast_pct = 0.0
            if len(prices) >= 5:
                forecast_pct = round(((prices.iloc[-1] - prices.iloc[-5]) / prices.iloc[-5]) * 100, 2)

            results.append({
                "Ticker": ticker,
                "Date": datetime.today().strftime("%Y-%m-%d"),
                "Forecast": forecast_pct,
                "Signal": signal
            })
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            continue

    return pd.DataFrame(results)
