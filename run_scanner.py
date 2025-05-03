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
from utils.helpers import aggregate_signals

# Optional user-defined setting (can be made dynamic later)
STEPS = 5

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
        df = yf.download(ticker, start=START_DATE, end=END_DATE, auto_adjust=True)

        print(f"\n📊 {ticker} columns: {df.columns.tolist()}")

        if df.empty:
            print(f"⚠️ No data for {ticker}. Skipping.")
            continue

        # Fallback logic
        if 'Adj Close' in df.columns:
            prices = df['Adj Close'].dropna().reset_index(drop=True)
        elif 'Close' in df.columns:
            print(f"⚠️ Using 'Close' instead of 'Adj Close' for {ticker}")
            prices = df['Close'].dropna().reset_index(drop=True)
        else:
            print(f"⚠️ No valid price column for {ticker}. Skipping.")
            continue

        preds = {
            "ARIMA": forecast_arima(prices, steps=STEPS),
            "GARCH": forecast_garch(prices, steps=STEPS),
            "HMM": forecast_hmm(prices, steps=STEPS),
            "LSTM": forecast_lstm(prices, steps=STEPS),
            "ML": forecast_ml(prices, steps=STEPS),
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
results_df = pd.DataFrame(results)

if results_df.empty:
    print("⚠️ No trade signals were generated. Writing empty CSV with headers.")
    results_df = pd.DataFrame(columns=["Ticker", "ARIMA", "GARCH", "HMM", "LSTM", "ML", "Final Signal"])

results_df.to_csv("data/top_trades.csv", index=False)
print("✅ Trade scan complete. Results saved to data/top_trades.csv")
