import os
import json
import pandas as pd
from datetime import datetime
from collections import Counter

from utils.common import fetch_price_data
from utils.helpers import load_config
from utils.sp500_tickers import get_sp500_tickers
from utils.tuner import load_model_weights, update_model_weights

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

# === Load configuration ===
config = load_config()
enabled_models = config["models"]
forecast_days = config["forecast_days"]
ticker_mode = config.get("ticker_mode", "sp500")

# === Load tickers ===
tickers = get_sp500_tickers()

# === Load model weights ===
model_weights = load_model_weights()

# === Helper: Regime classification ===
def classify_market_regime(df):
    df["return"] = df["Close"].pct_change()
    recent_return = df["return"].iloc[-20:].mean()
    if recent_return > 0.05:
        return "Bull"
    elif recent_return < -0.05:
        return "Bear"
    else:
        return "Neutral"

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
        confidence_scores = {}

        if enabled_models.get("arima"):
            try:
                pred, signal, conf = forecast_arima(ticker, df, forecast_days)
                predictions["ARIMA"] = signal
                confidence_scores["ARIMA"] = round(float(conf), 4)
            except Exception as e:
                predictions["ARIMA"] = f"ERROR: {e}"
                confidence_scores["ARIMA"] = 0

        if enabled_models.get("garch"):
            try:
                signal = forecast_garch(df, forecast_days)
                predictions["GARCH"] = signal
                confidence_scores["GARCH"] = 1
            except Exception as e:
                predictions["GARCH"] = f"ERROR: {e}"
                confidence_scores["GARCH"] = 0

        if enabled_models.get("hmm"):
            try:
                pred, signal, conf = forecast_hmm(ticker, df, forecast_days)
                predictions["HMM"] = signal
                confidence_scores["HMM"] = round(float(conf), 4)
            except Exception as e:
                predictions["HMM"] = f"ERROR: {e}"
                confidence_scores["HMM"] = 0

        if enabled_models.get("lstm"):
            try:
                pred, signal, conf = forecast_lstm(ticker, df, forecast_days)
                predictions["LSTM"] = signal
                confidence_scores["LSTM"] = round(float(conf), 4)
            except Exception as e:
                predictions["LSTM"] = f"ERROR: {e}"
                confidence_scores["LSTM"] = 0

        if enabled_models.get("ml"):
            try:
                signal = forecast_ml(df, forecast_days)
                predictions["XGBoost"] = signal
                confidence_scores["XGBoost"] = 1
            except Exception as e:
                predictions["XGBoost"] = f"ERROR: {e}"
                confidence_scores["XGBoost"] = 0

        # === Voting logic ===
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for model, signal in predictions.items():
            if signal in votes:
                weight = model_weights.get(model, 1.0)
                conf = confidence_scores.get(model, 1.0)
                votes[signal] += weight * conf

        final_signal = max(votes, key=votes.get) if any(votes.values()) else "HOLD"
        regime = classify_market_regime(df)

        rationale = f"Vote weights: {votes}. Adjusted for regime: {regime}."

        result = {
            "Ticker": ticker,
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Final Signal": final_signal,
            "Regime": regime,
            "Confidence": round(max(votes.values()), 4),
            "Rationale": rationale
        }
        result.update(predictions)
        forecast_results.append(result)

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# === Save Results ===
os.makedirs("data", exist_ok=True)
forecast_df = pd.DataFrame(forecast_results)
forecast_df.to_csv("data/top_trades.csv", index=False)
update_model_weights(forecast_df)

print("💾 Saved to data/top_trades.csv")
print("✅ Summary:")
print(forecast_df.head(5))
