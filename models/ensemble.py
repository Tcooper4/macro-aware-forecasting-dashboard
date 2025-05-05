import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml
from models.dynamic_tuner import load_model_weights
from utils.common import fetch_price_data

# === Load dynamic weights ===
MODEL_WEIGHTS = load_model_weights()

def classify_market_regime(df):
    df = df.copy()
    df["return"] = df["Close"].pct_change()
    recent_return = df["return"].iloc[-20:].mean()

    if recent_return > 0.05:
        return "Bull"
    elif recent_return < -0.05:
        return "Bear"
    else:
        return "Neutral"

def generate_forecast_ensemble(df, horizon="1 Week"):
    forecast_days = {
        "1 Day": 1,
        "1 Week": 5,
        "1 Month": 21
    }.get(horizon, 5)

    model_votes = {}
    confidence_scores = {}

    # === ARIMA ===
    try:
        pred_val, signal, conf = forecast_arima("TICKER", df, forecast_days)
        model_votes["ARIMA"] = signal
        confidence_scores["ARIMA"] = conf
    except Exception:
        model_votes["ARIMA"] = "ERROR"
        confidence_scores["ARIMA"] = 0

    # === GARCH ===
    try:
        signal = forecast_garch(df, forecast_days)
        model_votes["GARCH"] = signal
        confidence_scores["GARCH"] = 1  # Static confidence for GARCH
    except Exception:
        model_votes["GARCH"] = "ERROR"
        confidence_scores["GARCH"] = 0

    # === HMM ===
    try:
        pred_val, signal, conf = forecast_hmm("TICKER", df, forecast_days)
        model_votes["HMM"] = signal
        confidence_scores["HMM"] = conf
    except Exception:
        model_votes["HMM"] = "ERROR"
        confidence_scores["HMM"] = 0

    # === LSTM ===
    try:
        pred_val, signal, conf = forecast_lstm("TICKER", df, forecast_days)
        model_votes["LSTM"] = signal
        confidence_scores["LSTM"] = conf
    except Exception:
        model_votes["LSTM"] = "ERROR"
        confidence_scores["LSTM"] = 0

    # === ML Model (XGBoost) ===
    try:
        signal = forecast_ml(df, forecast_days)
        model_votes["XGBoost"] = signal
        confidence_scores["XGBoost"] = 1  # Static for now
    except Exception:
        model_votes["XGBoost"] = "ERROR"
        confidence_scores["XGBoost"] = 0

    # === Weighted Voting Logic ===
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for model, signal in model_votes.items():
        if signal in votes:
            weight = MODEL_WEIGHTS.get(model, 1.0)
            confidence = confidence_scores.get(model, 1.0)
            votes[signal] += weight * confidence

    final_signal = max(votes, key=votes.get) if any(votes.values()) else "HOLD"

    # === Regime Adjustment ===
    regime = classify_market_regime(df)
    if regime == "Bull" and final_signal == "HOLD":
        final_signal = "BUY"
    elif regime == "Bear" and final_signal == "HOLD":
        final_signal = "SELL"

    # === Forecast Table ===
    forecast_table = pd.DataFrame([
        {
            "Model": model,
            "Signal": signal,
            "Confidence": round(confidence_scores.get(model, 0), 4)
        }
        for model, signal in model_votes.items()
    ])

    rationale = f"Models voted: {dict(Counter(model_votes.values()))}. " \
                f"Confidence-weighted vote tally: {votes}. Adjusted for `{regime}` regime."

    return {
        "forecast_table": forecast_table,
        "final_signal": final_signal,
        "rationale": rationale
    }
