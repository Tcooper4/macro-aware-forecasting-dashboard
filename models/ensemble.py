# models/ensemble.py

from models.arima import arima_forecast_signal
from models.garch import garch_forecast_signal
from models.hmm import hmm_forecast_signal
from models.lstm import lstm_forecast_signal
from models.xgboost_model import xgboost_forecast_signal

from collections import Counter

def generate_ensemble_signal(ticker, start_date, end_date, settings=None):
    """
    Generate a final trading signal by combining multiple model outputs.

    Parameters:
    - ticker (str): Stock ticker.
    - start_date (str): Start date for historical data.
    - end_date (str): End date for historical data.
    - settings (dict): Optional settings for individual models.

    Returns:
    - dict: Final signal and individual model votes.
    """

    model_votes = {}

    try:
        model_votes["ARIMA"] = arima_forecast_signal(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["ARIMA"] = "ERROR"

    try:
        model_votes["GARCH"] = garch_forecast_signal(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["GARCH"] = "ERROR"

    try:
        model_votes["HMM"] = hmm_forecast_signal(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["HMM"] = "ERROR"

    try:
        model_votes["LSTM"] = lstm_forecast_signal(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["LSTM"] = "ERROR"

    try:
        model_votes["XGBoost"] = xgboost_forecast_signal(ticker, start_date, end_date, settings)
    except Exception as e:
        model_votes["XGBoost"] = "ERROR"

    # Filter out errored models
    valid_votes = [v for v in model_votes.values() if v in {"BUY", "HOLD", "SELL"}]

    if valid_votes:
        vote_counts = Counter(valid_votes)
        final_signal = vote_counts.most_common(1)[0][0]
    else:
        final_signal = "HOLD"  # default if all models fail

    return {
        "ticker": ticker,
        "final_signal": final_signal,
        "model_votes": model_votes
    }
