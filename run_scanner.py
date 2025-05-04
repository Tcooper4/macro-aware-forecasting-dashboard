import json
import pandas as pd
from datetime import datetime
from utils.helpers import (
    get_price_data,
    generate_signal,
    apply_signal_logic,
    load_tickers
)

# === Load configuration ===
with open("forecast_config.json", "r") as f:
    config = json.load(f)

models_config = config["models"]
signal_logic = config.get("signal_logic", "ensemble")
forecast_days = config.get("forecast_days", 5)
thresholds = config.get("thresholds", {"buy": 5.0, "sell": -5.0})
ticker_mode = config.get("ticker_mode", "sp500")

# === Load Tickers ===
if ticker_mode == "all":
    tickers = load_tickers(source="all")  # Implement this in helpers.py if not done
else:
    tickers = load_tickers(source="sp500")

# === Forecast and Signal Generation ===
forecast_results = []

print("📊 Scanning tickers for forecast signals...")

for ticker in tickers:
    try:
        df = get_price_data(ticker)

        if df is None or df.empty or "Close" not in df.columns:
            raise ValueError(f"Close price not found in yfinance data for {ticker}")

        signal, forecast_value = generate_signal(
            df,
            models_config=models_config,
            forecast_days=forecast_days,
            signal_logic=signal_logic
        )

        final_decision = apply_signal_logic(forecast_value, thresholds)

        forecast_results.append({
            "Ticker": ticker,
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Forecast": round(forecast_value, 2),
            "Signal": final_decision
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# === Save to CSV ===
result_df = pd.DataFrame(forecast_results)
result_df.to_csv("data/top_trades.csv", index=False)

print("💾 Results saved to data/top_trades.csv")
print("✅ Forecast Summary:")
print(result_df)
