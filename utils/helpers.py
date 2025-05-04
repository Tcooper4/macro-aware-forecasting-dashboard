import yfinance as yf
import pandas as pd
import numpy as np
import os
import json

def load_config(config_path="forecast_config.json"):
    """Load forecast configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ Config file not found. Using default settings.")
        return {
            "models": {
                "arima": True,
                "garch": True,
                "hmm": True,
                "lstm": True,
                "ml": True
            },
            "signal_logic": "ensemble",
            "forecast_days": 5,
            "thresholds": {
                "buy": 5.0,
                "sell": -5.0
            },
            "ticker_mode": "sp500"
        }

def load_tickers(source="sp500"):
    """Load tickers based on mode: 'sp500' or 'all' from tickers/all_tickers.txt"""
    if source == "all":
        try:
            with open("tickers/all_tickers.txt", "r") as f:
                tickers = [line.strip().upper() for line in f if line.strip()]
            return tickers
        except FileNotFoundError:
            print("❌ Error: 'tickers/all_tickers.txt' not found.")
            return []
    else:
        try:
            sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
            return sp500["Symbol"].tolist()
        except Exception as e:
            print(f"❌ Error loading S&P 500 tickers: {e}")
            return []

def get_price_data(ticker, period="1y", interval="1d"):
    """Download price data for a given ticker."""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            raise ValueError(f"No data for {ticker}")
        return df
    except Exception as e:
        print(f"❌ Error fetching price data for {ticker}: {e}")
        return None

def calculate_signal_from_models(predictions, logic="ensemble", thresholds={"buy": 5.0, "sell": -5.0}):
    """Combine multiple model predictions into a single signal."""
    signals = []

    # Normalize predictions
    clean_preds = [p for p in predictions if isinstance(p, (float, int, np.float64, np.int64))]

    if not clean_preds:
        return 0.0, "HOLD"

    if logic == "average":
        combined = np.mean(clean_preds)
    elif logic == "majority":
        combined = np.median(clean_preds)
    else:  # ensemble
        combined = np.average(clean_preds)

    if combined > thresholds["buy"]:
        decision = "BUY"
    elif combined < thresholds["sell"]:
        decision = "SELL"
    else:
        decision = "HOLD"

    return round(combined, 2), decision
