import pandas as pd
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

def generate_forecast_ensemble(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    results = {}

    results["ARIMA"] = forecast_arima(df, steps)
    results["GARCH"] = forecast_garch(df, steps)
    results["HMM"] = forecast_hmm(df, steps)
    results["LSTM"] = forecast_lstm(df, steps)
    results["XGBoost"] = forecast_ml(df, steps)

    forecast_df = pd.DataFrame(results)
    forecast_df["Average"] = forecast_df.mean(axis=1)

    last_price = df["Close"].iloc[-1]
    avg = forecast_df["Average"].iloc[-1]
    pct_change = (avg - last_price) / last_price

    if pct_change > 0.01:
        signal = "BUY"
    elif pct_change < -0.01:
        signal = "SELL"
    else:
        signal = "HOLD"

    forecast_df["Date"] = pd.date_range(start=df.index[-1], periods=steps + 1, freq="B")[1:]
    return {
        "forecast_table": forecast_df[["Date"] + list(results.keys()) + ["Average"]],
        "final_signal": signal,
        "rationale": f"Expected return: {pct_change:.2%}"
    }
