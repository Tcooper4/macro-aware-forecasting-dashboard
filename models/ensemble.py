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
from utils.common import fetch_price_data

# === Optional model weights (customize if desired) ===
MODEL_WEIGHTS = {
    "ARIMA": 1.0,
    "GARCH": 1.0,
    "HMM": 1.0,
    "LSTM": 1.0,
    "XGBoost": 1.0,
}

# === Market regime classification (stub) ===
def classify_market_regime(df):
    recent_return = df['Close'].pct_change(10).iloc[-1]
    if recent_return > 0.05:
        return "Bull"
    elif recent_return < -0.05:
        return "Bear"
    else:
        return "Neutral"

# === Final signal generator ===
def generate_forecast_ensemble(df, horizon="1 Week"):
    forecast_days = {
        "1 Day": 1,
        "1 Week": 5,
        "1 Month": 21
    }.get(horizon, 5)

    model_votes = {}
    confidence_scores = {}

    try:
        pred_val, signal = forecast_arima("TICKER", df, forecast_days)
        model_votes["ARIMA"] = signal
        confidence_scores["ARIMA"] = abs(pred_val)
    except Exception:
        model_votes["ARIMA"] = "ERROR"
        confidence_scores["ARIMA"] = 0

    try:
        signal = forecast_garch(df, forecast_days)
        model_votes["GARCH"] = signal
        confidence_scores["GARCH"] = 1
    except Exception:
        model_votes["GARCH"] = "ERROR"
        confidence_scores["GARCH"] = 0

    try:
        pred_val, signal = forecast_hmm("TICKER", df, forecast_days)
        model_votes["HMM"] = signal
        confidence_scores["HMM"] = abs(pred_val)
    except Exception:
        model_votes["HMM"] = "ERROR"
        confidence_scores["HMM"] = 0

    try:
        pred_val, signal = forecast_lstm("TICKER", df, forecast_days)
        model_votes["LSTM"] = signal
        confidence_scores["LSTM"] = abs(pred_val)
    except Exception:
        model_votes["LSTM"] = "ERROR"
        confidence_scores["LSTM"] = 0

    try:
        signal = forecast_ml(df, forecast_days)
        model_votes["XGBoost"] = signal
        confidence_scores["XGBoost"] = 1
    except Exception:
        model_votes["XGBoost"] = "ERROR"
        confidence_scores["XGBoost"] = 0

    # === Weighted Voting ===
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    for model, signal in model_votes.items():
        if signal in votes:
            weight = MODEL_WEIGHTS.get(model, 1.0)
            confidence = confidence_scores.get(model, 1.0)
            votes[signal] += weight * confidence

    final_signal = max(votes, key=votes.get) if any(votes.values()) else "HOLD"

    # === Regime boost ===
    regime = classify_market_regime(df)
    if regime == "Bull" and final_signal == "HOLD":
        final_signal = "BUY"
    elif regime == "Bear" and final_signal == "HOLD":
        final_signal = "SELL"

    # === Table output ===
    forecast_table = pd.DataFrame([{
        "Model": model,
        "Signal": signal,
        "Confidence": round(confidence_scores.get(model, 0), 4)
    } for model, signal in model_votes.items()])

    rationale = f"Models voted: {dict(Counter(model_votes.values()))}. Confidence-weighted vote tally: {votes}. Adjusted for `{regime}` regime."

    return {
        "forecast_table": forecast_table,
        "final_signal": final_signal,
        "rationale": rationale
    }
