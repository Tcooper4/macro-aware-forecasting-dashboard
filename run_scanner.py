import json
import pandas as pd
from datetime import datetime
from utils.helpers import (
    load_config, get_ticker_list,
    fetch_price_data, save_trade_results,
    generate_combined_signal
)

print("📊 Scanning tickers for forecast signals...")

config = load_config("forecast_config.json")
tickers = get_ticker_list(config["ticker_source"])

results = []

for ticker in tickers:
    try:
        prices = fetch_price_data(ticker)
        signal, forecast_value = generate_combined_signal(
            prices,
            config["models"],
            config["signal_thresholds"]
        )
        results.append({
            "Ticker": ticker,
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Forecast": forecast_value,
            "Signal": signal
        })
    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

df = pd.DataFrame(results)
print("💾 Saving results to data/top_trades.csv...")
save_trade_results(df)
print("✅ Forecast Summary:")
print(df)
