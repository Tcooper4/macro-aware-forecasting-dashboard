# ensemble.py (patched)
import sys, os
import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml
from models.dynamic_tuner import load_model_weights
from utils.common import fetch_price_data

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

def clean_signal(signal):
    if isinstance(signal, str) and signal in {"BUY", "SELL", "HOLD"}:
        return signal
    if isinstance(signal, tuple):
        for item in signal:
            if isinstance(item, str) and item in {"BUY", "SELL", "HOLD"}:
                return item
    return "ERROR"

def generate_forecast_ensemble(df, horizon="1 Week"):
    forecast_days = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)

    model_votes = {}
    confidence_scores = {}

    try:
        pred, signal, conf = forecast_arima("TICKER", df, forecast_days)
        model_votes["ARIMA"] = clean_signal(signal)
        confidence_scores["ARIMA"] = conf
    except Exception:
        model_votes["ARIMA"] = "ERROR"
        confidence_scores["ARIMA"] = 0

    try:
        signal = forecast_garch(df, forecast_days)
        model_votes["GARCH"] = clean_signal(signal)
        confidence_scores["GARCH"] = 1
    except Exception:
        model_votes["GARCH"] = "ERROR"
        confidence_scores["GARCH"] = 0

    try:
        pred, signal, conf = forecast_hmm("TICKER", df, forecast_days)
        model_votes["HMM"] = clean_signal(signal)
        confidence_scores["HMM"] = conf
    except Exception:
        model_votes["HMM"] = "ERROR"
        confidence_scores["HMM"] = 0

    try:
        pred, signal, conf = forecast_lstm("TICKER", df, forecast_days)
        model_votes["LSTM"] = clean_signal(signal)
        confidence_scores["LSTM"] = conf
    except Exception:
        model_votes["LSTM"] = "ERROR"
        confidence_scores["LSTM"] = 0

    try:
        pred, signal, conf = forecast_ml(df, forecast_days)
        model_votes["XGBoost"] = clean_signal(signal)
        confidence_scores["XGBoost"] = conf
    except Exception:
        model_votes["XGBoost"] = "ERROR"
        confidence_scores["XGBoost"] = 0

    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for model, signal in model_votes.items():
        if signal in votes:
            w = MODEL_WEIGHTS.get(model, 1.0)
            c = confidence_scores.get(model, 1.0)
            votes[signal] += w * c

    final_signal = max(votes, key=votes.get) if any(votes.values()) else "HOLD"

    regime = classify_market_regime(df)
    if regime == "Bull" and final_signal == "HOLD":
        final_signal = "BUY"
    elif regime == "Bear" and final_signal == "HOLD":
        final_signal = "SELL"

    forecast_table = pd.DataFrame([
        {"Model": model, "Signal": sig, "Confidence": round(confidence_scores.get(model, 0), 4)}
        for model, sig in model_votes.items()
    ])

    rationale = f"Models voted: {dict(Counter([str(sig) for sig in model_votes.values()]))}. " \
                f"Confidence-weighted vote tally: { {k: round(v, 4) for k, v in votes.items()} }. Adjusted for `{regime}` regime."

    return {
        "forecast_table": forecast_table,
        "final_signal": final_signal,
        "rationale": rationale,
        "model_confidences": confidence_scores
    }
