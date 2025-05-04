import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_model import forecast_ml

def load_config(path="forecast_config.json"):
    with open(path, "r") as f:
        return json.load(f)

def get_ticker_list(source: str) -> list:
    if source.lower() == "sp500":
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM",
            "V", "UNH", "PG", "MA", "DIS", "HD", "PEP", "KO", "WMT", "NFLX",
            "INTC", "ADBE"
        ]
    else:
        return [source.upper()]

def fetch_price_data(ticker: str, start_date="2020-01-01", end_date=None):
    if end_date is None:
        end_date = pd.to_datetime("today").strftime("%Y-%m-%d")
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    if "Close" not in df.columns:
        raise ValueError(f"Close price not found in yfinance data for {ticker}")
    return df["Close"]

def generate_combined_signal(prices: pd.Series, model_flags: dict, thresholds: dict) -> tuple:
    forecasts = []

    if model_flags.get("arima"):
        try:
            forecasts.append(forecast_arima(prices))
        except Exception as e:
            print(f"ARIMA failed for {prices.name}: {e}")
    if model_flags.get("garch"):
        try:
            forecasts.append(forecast_garch(prices))
        except Exception as e:
            print(f"GARCH failed for {prices.name}: {e}")
    if model_flags.get("hmm"):
        try:
            forecasts.append(forecast_hmm(prices))
        except Exception as e:
            print(f"HMM failed for {prices.name}: {e}")
    if model_flags.get("lstm"):
        try:
            forecasts.append(forecast_lstm(prices))
        except Exception as e:
            print(f"LSTM failed for {prices.name}: {e}")
    if model_flags.get("ml"):
        try:
            forecasts.append(forecast_ml(prices))
        except Exception as e:
            print(f"ML failed for {prices.name}: {e}")

    if not forecasts:
        return "HOLD", 0.0

    avg_forecast = sum(forecasts) / len(forecasts)

    if avg_forecast > thresholds["buy"]:
        signal = "BUY"
    elif avg_forecast < thresholds["sell"]:
        signal = "SELL"
    else:
        signal = "HOLD"

    return signal, round(avg_forecast * 100, 2)

def save_trade_results(df: pd.DataFrame, file_path="data/top_trades.csv"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
