import yfinance as yf
import pandas as pd
import numpy as np
import json
from models.ensemble import ensemble_signal

def get_price_data(ticker, period="2y", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        df.dropna(inplace=True)
        if "Close" not in df.columns:
            return None
        return df
    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return None

def load_config(path="forecast_config.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}

def load_tickers(mode="sp500"):
    sp500 = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "UNH",
        "PG", "MA", "DIS", "HD", "PEP", "KO", "WMT", "NFLX", "INTC", "ADBE"
    ]
    if mode == "sp500":
        return sp500
    elif mode == "all":
        # You can expand this list or load dynamically from a file or API if needed
        return sp500  # Placeholder: replace with full ticker list as needed
    else:
        return sp500

def calculate_signal_from_models(predictions, logic, thresholds):
    """
    predictions: dict with model_name -> forecast value
    logic: 'ensemble', 'average', or 'majority'
    thresholds: dict with 'buy' and 'sell' levels
    """
    # Remove invalid or NaN forecasts
    valid_preds = {k: v for k, v in predictions.items() if v is not None and not np.isnan(v)}

    if not valid_preds:
        return 0.0, "HOLD"

    if logic == "ensemble":
        return ensemble_signal(valid_preds, thresholds)

    elif logic == "average":
        avg = np.mean(list(valid_preds.values()))
        if avg >= thresholds["buy"]:
            return avg, "BUY"
        elif avg <= thresholds["sell"]:
            return avg, "SELL"
        else:
            return avg, "HOLD"

    elif logic == "majority":
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for val in valid_preds.values():
            if val >= thresholds["buy"]:
                votes["BUY"] += 1
            elif val <= thresholds["sell"]:
                votes["SELL"] += 1
            else:
                votes["HOLD"] += 1
        signal = max(votes, key=votes.get)
        avg = np.mean(list(valid_preds.values()))
        return avg, signal

    else:
        # Default fallback
        avg = np.mean(list(valid_preds.values()))
        return avg, "HOLD"
