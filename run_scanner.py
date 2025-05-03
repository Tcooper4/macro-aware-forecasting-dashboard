import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from tqdm import tqdm

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml
from utils.helpers import fetch_price_data
from utils.expert import get_expert_settings
from models.ensemble import generate_ensemble_signal  # Optional: not used below

# --- Configuration ---
TICKERS = [
    "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A"
]
START_DATE = (datetime.today() - timedelta(days=3 * 365)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')

# --- Result Store ---
results = []

# --- Main Scanning Loop ---
for ticker in tqdm(TICKERS, desc="📈 Scanning tickers"):
    try:
        df = yf.download(ticker, start=START_DATE, end=END_DATE)
        if df.empty or ('Adj Close' not in df.columns and 'Close' not in df.columns):
            print(f"⚠️ No valid data for {ticker}. Columns found: {df.columns.tolist()}")
            continue

        prices = df['Adj Close'].dropna() if 'Adj Close' in df.columns else df['Close'].dropna()
        prices = prices.reset_index(drop=True)

        preds = {
            "ARIMA": forecast_arima(prices),
            "GARCH": forecast_garch(prices),
            "HMM": forecast_hmm(prices),
            "LSTM": forecast_lstm(prices),
            "ML": forecast_ml(prices),
        }

        def aggregate_signals(predictions: dict):
            from collections import Counter
            votes = [p for p in predictions.values() if p in {"BUY", "HOLD", "SELL"}]
            return Counter(votes).most_common(1)[0][0] if votes else "HOLD"

        final_signal = aggregate_signals(preds)
        print(f"✅ {ticker} - Predictions: {preds} → Final: {final_signal}")

        results.append({
            "Ticker": ticker,
            **preds,
            "Final Signal": final_signal
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# --- Output Results ---
os.makedirs("data", exist_ok=True)
columns = ["Ticker", "ARIMA", "GARCH", "HMM", "LSTM", "ML", "Final Signal"]
results_df = pd.DataFrame(results, columns=columns)
results_df.to_csv("data/top_trades.csv", index=False)

print(f"🔍 Total successful trades: {len(results)}")
print("✅ Trade scan complete. Results saved to data/top_trades.csv")
