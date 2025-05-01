import pandas as pd
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

def generate_forecast_ensemble(df, horizon="1 Week"):
    recent_data = df.copy()
    results = {}

    results["ARIMA"] = forecast_arima(recent_data, horizon)
    results["GARCH"] = forecast_garch(recent_data, horizon)
    results["HMM"] = forecast_hmm(recent_data, horizon)
    results["LSTM"] = forecast_lstm(recent_data, horizon)
    results["XGBoost"] = forecast_ml(recent_data, horizon)

    forecast_df = pd.DataFrame(results)
    forecast_df["Average"] = forecast_df.mean(axis=1)

    last_row = forecast_df.iloc[-1]
    avg_forecast = last_row["Average"]
    current_price = recent_data["Close"].iloc[-1]
    pct_change = (avg_forecast - current_price) / current_price

    if pct_change > 0.01:
        signal = "BUY"
        reason = "Most models forecast a strong upward trend."
    elif pct_change < -0.01:
        signal = "SELL"
        reason = "Most models forecast a significant drop."
    else:
        signal = "HOLD"
        reason = "No strong directional forecast — best to wait."

    forecast_df["Date"] = recent_data.index[-len(forecast_df):]
    forecast_df = forecast_df[["Date"] + list(results.keys()) + ["Average"]]

    return {
        "forecast_table": forecast_df,
        "final_signal": signal,
        "rationale": f"Expected return: {pct_change:.2%}. {reason}"
    }
