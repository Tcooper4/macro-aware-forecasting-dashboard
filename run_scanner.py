from utils.trade_scanner import scan_sp500_for_trades

# Run the scanner and save top N trade picks to CSV
scan_sp500_for_trades(horizon="1 Week", top_n=10)
print("✅ Trade scan complete. Results saved to data/top_trades.csv")
