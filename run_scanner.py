import os
import pandas as pd
from tqdm import tqdm

from utils.helpers import fetch_price_data, save_trade_results
from models.arima_model import forecast_arima
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm

# --- Settings ---
tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META", "TSLA", "NVDA",
    "JPM", "V", "UNH"
]
forecast_steps = 5
output_file = "data/top_trades.csv"

# Optional weights for ensemble voting (must sum to 1)
weights = {
    'ARIMA': 0.3,
    'HMM': 0.3,
    'LSTM': 0.4
}

results = []

print("📈 Scanning tickers...")
for ticker in tqdm(tickers):
    try:
        df = fetch_price_data(ticker)

        # Forecast with each model
        arima_ret, arima_signal = forecast_arima(ticker, df, forecast_steps)
        hmm_ret, hmm_signal = forecast_hmm(ticker, df, forecast_steps)
        lstm_ret, lstm_signal = forecast_lstm(ticker, df, forecast_steps)

        # Score signals for ensemble logic
        score_map = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
        signals = {
            'ARIMA': arima_signal,
            'HMM': hmm_signal,
            'LSTM': lstm_signal
        }

        weighted_score = sum(weights[model] * score_map[sig] for model, sig in signals.items())
        final_signal = (
            'BUY' if weighted_score > 0.25 else
            'SELL' if weighted_score < -0.25 else
            'HOLD'
        )

        print(f"🧠 {ticker}: {signals} -> Final Signal: {final_signal}")

        results.append({
            'Ticker': ticker,
            'ARIMA Signal': arima_signal,
            'HMM Signal': hmm_signal,
            'LSTM Signal': lstm_signal,
            'Final Signal': final_signal,
            'ARIMA Return': arima_ret,
            'HMM Return': hmm_ret,
            'LSTM Return': lstm_ret
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# Save results
df_results = pd.DataFrame(results)
df_results.to_csv(output_file, index=False)
print(f"✅ Trade scan complete. Results saved to {output_file}")
