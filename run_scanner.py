import os
import json
import pandas as pd
from datetime import datetime
from utils.helpers import (
    get_price_data,
    load_tickers,
    load_config,
    calculate_signal_from_models
)
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

# === Load configuration ===
with open("forecast_config.json") as f:
    config = json.load(f)

enabled_models = config["models"]
logic = config["signal_logic"]
forecast_days = config["forecast_days"]
thresholds = config["thresholds"]
ticker_mode = config.get("ticker_mode", "sp500")  # "sp500" or "all"

# === Load tickers ===
tickers = load_tickers(mode=ticker_mode)

# === Forecast loop ===
forecast_results = []

print("📊 Scanning tickers for forecast signals...")
for ticker in tickers:
    try:
        df = get_price_data(ticker)
        if df is None or df.empty or "Close" not in df.columns:
            print(f"❌ Error: No valid price data for {ticker}")
            continue

        predictions = {}

        if enabled_models.get("arima"):
            predictions["arima"] = forecast_arima(df, forecast_days)

        if enabled_models.get("garch"):
            predictions["garch"] = forecast_garch(df, forecast_days)

        if enabled_models.get("hmm"):
            predictions["hmm"] = forecast_hmm(df, forecast_days)

        if enabled_models.get("lstm"):
            predictions["lstm"] = forecast_lstm(df, forecast_days)

        if enabled_models.get("ml"):
            predictions["ml"] = forecast_ml(df, forecast_days)

        forecast, signal = calculate_signal_from_models(predictions, logic, thresholds)

        forecast_results.append({
            "Ticker": ticker,
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Forecast": round(forecast, 2),
            "Signal": signal
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# === Save results ===
forecast_df = pd.DataFrame(forecast_results)
forecast_df.to_csv("data/top_trades.csv", index=False)

print("💾 Saved results to data/top_trades.csv")
print("✅ Forecast Summary:")
print(forecast_df)
