# run_scanner.py

import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from tqdm import tqdm
from collections import Counter

from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import forecast_hmm
from models.lstm_model import forecast_lstm
from models.ml_models import forecast_ml

# --- Aggregate Signals ---
def aggregate_signals(predictions):
    """
    Aggregate signals from multiple models using majority vote.
    """
    votes = [v for v in predictions.values() if v in ["BUY", "SELL", "HOLD"]]
    if not votes:
        return "HOLD"
    return Counter(votes).most_common(1)[0][0]

# --- Tickers and Dates ---
TICKERS = ["MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A"]
START_DATE = (datetime.today() - timedelta(days=3 * 365)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')

# --- Store Results ---
results = []

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

        print(f"\n✅ {ticker} model predictions:")
        for model, signal in preds.items():
            print(f"  {model}: {signal}")

        final_signal = aggregate_signals(preds)

        results.append({
            "Ticker": ticker,
            **preds,
            "Final Signal": final_signal
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

# --- Save Results ---
os.makedirs("data", exist_ok=True)
results_df = pd.DataFrame(results)
results_df.to_csv("data/top_trades.csv", index=False)

print("\n📊 Final DataFrame:")
print(results_df)
print("✅ Trade scan complete. Results saved to data/top_trades.csv")
