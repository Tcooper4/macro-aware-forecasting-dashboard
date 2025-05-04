import os
import json
import pandas as pd
from datetime import datetime
from models.ensemble import generate_ensemble_signal
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml
from utils.common import fetch_price_data, generate_signal_from_return

def load_config():
    config_path = os.path.join("config", "forecast_config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def run_model_forecasts(ticker, start_date, end_date, config):
    models = config.get("models", {})
    thresholds = config.get("thresholds", {"buy": 5.0, "sell": -5.0})
    days = config.get("forecast_days", 5)

    results = {}

    if models.get("arima"):
        try:
            results["arima"] = forecast_arima(ticker, start_date, end_date, days, thresholds)
        except Exception as e:
            results["arima"] = {"signal": "ERROR", "return": None}

    if models.get("garch"):
        try:
            results["garch"] = forecast_garch(ticker, start_date, end_date, days, thresholds)
        except Exception as e:
            results["garch"] = {"signal": "ERROR", "return": None}

    if models.get("hmm"):
        try:
            results["hmm"] = forecast_hmm(ticker, start_date, end_date, days, thresholds)
        except Exception as e:
            results["hmm"] = {"signal": "ERROR", "return": None}

    if models.get("lstm"):
        try:
            results["lstm"] = forecast_lstm(ticker, start_date, end_date, days, thresholds)
        except Exception as e:
            results["lstm"] = {"signal": "ERROR", "return": None}

    if models.get("ml"):
        try:
            results["ml"] = forecast_ml(ticker, start_date, end_date, days, thresholds)
        except Exception as e:
            results["ml"] = {"signal": "ERROR", "return": None}

    return results

def generate_signal(ticker, start_date, end_date, config):
    logic = config.get("signal_logic", "ensemble")

    if logic == "ensemble":
        signal_data = generate_ensemble_signal(ticker, start_date, end_date, config)
        return signal_data["final_signal"], signal_data["model_votes"]
    
    results = run_model_forecasts(ticker, start_date, end_date, config)
    signal_counts = {}
    signal_sum = 0
    count = 0

    for model, data in results.items():
        signal = data.get("signal")
        model_return = data.get("return")

        if logic == "majority" and signal in {"BUY", "HOLD", "SELL"}:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1

        elif logic == "average" and model_return is not None:
            signal_sum += model_return
            count += 1

    if logic == "majority" and signal_counts:
        final_signal = max(signal_counts, key=signal_counts.get)
    elif logic == "average" and count > 0:
        avg_return = signal_sum / count
        final_signal = generate_signal_from_return(avg_return, config.get("thresholds", {}))
    else:
        final_signal = "HOLD"

    return final_signal, results
