from utils.helpers import fetch_price_data, generate_forecast_signal, save_trade_results, aggregate_signals
import pandas as pd

# Define the list of tickers you want to scan
tickers_to_scan = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "UNH",
    "PG", "MA", "DIS", "HD", "PEP", "KO", "WMT", "NFLX", "INTC", "ADBE"
]

# Aggregate signals for the defined tickers
trade_signals_df = aggregate_signals(tickers_to_scan)

# Display output to console (optional)
print(trade_signals_df)

# Save to CSV
save_trade_results(trade_signals_df, file_path="data/top_trades.csv")
