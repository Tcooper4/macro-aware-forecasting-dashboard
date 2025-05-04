import os
import json
import pandas as pd
from datetime import datetime
from utils.common import fetch_price_data
from utils.helpers import load_config
from utils.sp500_tickers import get_sp500_tickers

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

from collections import Counter

# === Load configuration ===
config = load_config()
enabled_models = config["models"]
logic = config["signal_logic"]  # Currently unused
forecast_days = config["forecast_days"]
thresholds = config["thresholds"]  # Currently unused
ticker_mode = config.get("ticker_mode", "sp500")  # Only supports "sp500"

# === Load tickers ===
tickers = get_sp500_tickers()

# === Forecast loop ===
forecast_results = []

print("📊 Scanning tickers for forecast signals...")
for ticker in tickers:
    try:
        df = fetch_price_data(ticker, start_date="2020-01-01", end_date=datetime.today().strftime("%Y-%m-%d"))
        if df is None or df.empty or "Close" not in df.columns:
            print(f"❌ Error: No valid price data for {ticker}")
            continue

        predictions = {}

        if enabled_models.get("arima"):
            _, predictions["ARIMA"] = forecast_arima(ticker, df, forecast_days)

        if enabled_models.get("garch"):
            try:
                predictions["GARCH"] = forecast_garch(df, forecast_days)
            except Exception as e:
                predictions["GARCH"] = f"ERROR: {e}"

        if enabled_models.get("hmm"):
            try:
                _, predictions["HMM"] = forecast_hmm(ticker, df, forecast_days)
            except Exception as e:
                predictions["HMM"] = f"ERROR: {e}"

        if enabled_models.get("lstm"):
            try:
                _, predictions["LSTM"] = forecast_lstm(ticker, df, forecast_days)
            except Exception as e:
                predictions["LSTM"] = f"ERROR: {e}"

        if enabled_models.get("ml"):
            try:
                predictions["XGBoost"] = forecast_ml(df, forecast_days)
            except Exception as e:
                predictions["XGBoost"] = f"ERROR: {e}"

        # Count only valid signals (BUY, SELL, HOLD)
        vote_counts = Counter([v for v in predictions.values() if v in {"BUY", "SELL", "HOLD"}])
        final_signal = vote_counts.most_common(1)[0][0] if vote_counts else "HOLD"

        result = {
            "Ticker": ticker,
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Final Signal": final_signal
        }
        result.update(predictions)
        forecast_results.append(result)

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# === Save results ===
os.makedirs("data", exist_ok=True)
forecast_df = pd.DataFrame(forecast_results)
forecast_df = forecast_df[forecast_df["Final Signal"] == "BUY"]  # Filter if desired
forecast_df.to_csv("data/top_trades.csv", index=False)

print("💾 Saved results to data/top_trades.csv")
print("✅ Forecast Summary:")
print(forecast_df)
