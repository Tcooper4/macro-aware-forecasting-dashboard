# run_scanner.py

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
from models.ensemble import generate_ensemble_signal

# --- Configuration ---
TICKERS = ["MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A"]
START_DATE = (datetime.today() - timedelta(days=3 * 365)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Set a shared forecast horizon
FORECAST_STEPS = 5  # or pull from user config later

# --- Result Store ---
results = []

# --- Helper Function ---
def aggregate_signals(preds):
    """Vote majority mechanism"""
    votes = [signal for signal in preds.values() if signal in {"BUY", "HOLD", "SELL"}]
    if not votes:
        return "HOLD"
    return max(set(votes), key=votes.count)

# --- Main Scanning Loop ---
for ticker in tqdm(TICKERS, desc="📈 Scanning tickers"):
    try:
        df = yf.download(ticker, start=START_DATE, end=END_DATE, auto_adjust=True)
        if df.empty or 'Adj Close' not in df.columns:
            print(f"⚠️ No valid data for {ticker}. Skipping.")
            continue

        prices = df['Adj Close'].dropna().reset_index(drop=True)

        preds = {
            "ARIMA": forecast_arima(prices, FORECAST_STEPS),
            "GARCH": forecast_garch(prices, FORECAST_STEPS),
            "HMM": forecast_hmm(prices, FORECAST_STEPS),
            "LSTM": forecast_lstm(prices, FORECAST_STEPS),
            "ML": forecast_ml(prices, FORECAST_STEPS),
        }

        final_signal = aggregate_signals(preds)

        results.append({
            "Ticker": ticker,
            **preds,
            "Final Signal": final_signal
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# --- Output Results ---
os.makedirs("data", exist_ok=True)

if results:
    results_df = pd.DataFrame(results)
    print("📊 Final Results Preview:")
    print(results_df.head())
    results_df.to_csv("data/top_trades.csv", index=False)
else:
    print("⚠️ No trade signals were generated. Writing empty CSV with headers.")
    pd.DataFrame(columns=["Ticker", "ARIMA", "GARCH", "HMM", "LSTM", "ML", "Final Signal"]).to_csv("data/top_trades.csv", index=False)

print("✅ Trade scan complete. Results saved to data/top_trades.csv")
