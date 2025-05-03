import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

from collections import Counter

def generate_ensemble_signal(ticker, start_date, end_date, settings=None):
    model_votes = {}

    try:
        model_votes["ARIMA"] = forecast_arima(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["ARIMA"] = "ERROR"

    try:
        model_votes["GARCH"] = forecast_garch(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["GARCH"] = "ERROR"

    try:
        model_votes["HMM"] = forecast_hmm(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["HMM"] = "ERROR"

    try:
        model_votes["LSTM"] = forecast_lstm(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["LSTM"] = "ERROR"

    try:
        model_votes["XGBoost"] = forecast_ml(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["XGBoost"] = "ERROR"

    valid_votes = [v for v in model_votes.values() if v in {"BUY", "HOLD", "SELL"}]

    if valid_votes:
        vote_counts = Counter(valid_votes)
        final_signal = vote_counts.most_common(1)[0][0]
    else:
        final_signal = "HOLD"

    return {
        "ticker": ticker,
        "final_signal": final_signal,
        "model_votes": model_votes
    }
