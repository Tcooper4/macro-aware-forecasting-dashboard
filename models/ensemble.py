import pandas as pd
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml
from sklearn.preprocessing import KBinsDiscretizer
from utils.expert import get_expert_settings

def classify_market_regime(df):
    """Uses HMM to classify market regime: Bull, Bear, or Volatile"""
    import numpy as np
    from hmmlearn.hmm import GaussianHMM

    log_returns = np.log(df["Close"] / df["Close"].shift(1)).dropna().values.reshape(-1, 1)
    if len(log_returns) < 60:
        return "Neutral"

    model = GaussianHMM(n_components=3, covariance_type="diag", n_iter=1000)
    model.fit(log_returns)
    hidden_states = model.predict(log_returns)
    last_state = hidden_states[-1]

    # Assign regime labels based on state volatility
    vol_per_state = {
        state: np.std(log_returns[hidden_states == state])
        for state in np.unique(hidden_states)
    }
    sorted_states = sorted(vol_per_state.items(), key=lambda x: x[1])
    labels = ["Bull", "Neutral", "Bear"]  # lowest vol → highest vol

    state_map = {state: labels[i] for i, (state, _) in enumerate(sorted_states)}
    return state_map[last_state]

def regime_weight(signal, regime):
    """Adjust signal weighting or override based on regime"""
    if regime == "Bull" and signal == "BUY":
        return "BUY"
    elif regime == "Bear" and signal == "BUY":
        return "HOLD"
    elif regime == "Bear" and signal == "HOLD":
        return "SELL"
    else:
        return signal

def generate_forecast_ensemble(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    results = {}

    close_series = df["Close"]

    results["ARIMA"] = forecast_arima(close_series, steps)
    results["GARCH"] = forecast_garch(close_series, steps)
    results["HMM"] = forecast_hmm(close_series, steps)
    results["LSTM"] = forecast_lstm(close_series, steps)
    results["ML"] = forecast_ml(close_series, steps)

    forecast_df = pd.DataFrame(results)
    forecast_df["Average"] = forecast_df.mean(axis=1)

    last_price = close_series.iloc[-1]
    predicted = forecast_df["Average"].iloc[-1]
    change = (predicted - last_price) / last_price

    if change > 0.01:
        raw_signal = "BUY"
    elif change < -0.01:
        raw_signal = "SELL"
    else:
        raw_signal = "HOLD"

    regime = classify_market_regime(df)
    adjusted_signal = regime_weight(raw_signal, regime)

    forecast_df["Date"] = pd.date_range(start=df.index[-1], periods=steps + 1, freq="B")[1:]

    return {
        "forecast_table": forecast_df[["Date"] + list(results.keys()) + ["Average"]],
        "final_signal": adjusted_signal,
        "rationale": f"Model signal was `{raw_signal}`, but adjusted to `{adjusted_signal}` based on `{regime}` regime.",
        "regime": regime
    }
