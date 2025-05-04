import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

from collections import Counter

from datetime import datetime
from utils.common import fetch_price_data

def generate_ensemble_signal(ticker, start_date="2020-01-01", end_date=None, settings=None):
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    forecast_days = settings.get("forecast_days", 5) if settings else 5
    df = fetch_price_data(ticker, start_date, end_date)

    if df is None or df.empty:
        return {
            "ticker": ticker,
            "final_signal": "HOLD",
            "model_votes": {model: "ERROR" for model in ["ARIMA", "GARCH", "HMM", "LSTM", "XGBoost"]}
        }

    model_votes = {}

    try:
        _, model_votes["ARIMA"] = forecast_arima(ticker, df, forecast_days)
    except Exception:
        model_votes["ARIMA"] = "ERROR"

    try:
        model_votes["GARCH"] = forecast_garch(df, forecast_days)
    except Exception:
        model_votes["GARCH"] = "ERROR"

    try:
        _, model_votes["HMM"] = forecast_hmm(ticker, df, forecast_days)
    except Exception:
        model_votes["HMM"] = "ERROR"

    try:
        _, model_votes["LSTM"] = forecast_lstm(ticker, df, forecast_days)
    except Exception:
        model_votes["LSTM"] = "ERROR"

    try:
        model_votes["XGBoost"] = forecast_ml(df, forecast_days)
    except Exception:
        model_votes["XGBoost"] = "ERROR"

    # === Final Signal via Voting ===
    from collections import Counter
    valid_votes = [v for v in model_votes.values() if v in {"BUY", "SELL", "HOLD"}]
    final_signal = Counter(valid_votes).most_common(1)[0][0] if valid_votes else "HOLD"

    return {
        "ticker": ticker,
        "final_signal": final_signal,
        "model_votes": model_votes
    }
