import pandas as pd
from utils.helpers import aggregate_signals, save_trade_results

import json

with open("forecast_config.json", "r") as f:
    config = json.load(f)

ENABLED_MODELS = config["models"]
SIGNAL_LOGIC = config["signal_logic"]
FORECAST_DAYS = config["forecast_days"]
THRESHOLDS = config["thresholds"]

# Define the tickers to scan (S&P 500 subset or full list later)
tickers_to_scan = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    "JPM", "V", "UNH", "PG", "MA", "DIS", "HD", "PEP", "KO",
    "WMT", "NFLX", "INTC", "ADBE"
]

# Step 1: Aggregate forecast signals
print("📊 Scanning tickers for forecast signals...")
df_signals = aggregate_signals(tickers_to_scan)

# Step 2: Save results to CSV
print("💾 Saving results to data/top_trades.csv...")
save_trade_results(df_signals)

# Step 3: Print results to console
print("✅ Forecast Summary:")
print(df_signals)
