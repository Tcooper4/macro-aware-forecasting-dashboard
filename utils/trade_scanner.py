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
from models.ensemble import generate_ensemble_signal
from utils.helpers import fetch_price_data
from utils.expert import get_expert_settings


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
        if df.empty or 'Adj Close' not in df.columns:
            print(f"⚠️ No valid data for {ticker}. Skipping.")
            continue

        prices = df['Adj Close'].dropna().reset_index(drop=True)

        preds = {
            "ARIMA": forecast_arima(prices),
            "GARCH": forecast_garch(prices),
            "HMM": forecast_hmm(prices),
            "LSTM": forecast_lstm(prices),
            "ML": forecast_ml(prices),
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
results_df.to_csv("data/top_trades.csv", index=False)

print("✅ Trade scan complete. Results saved to data/top_trades.csv")
