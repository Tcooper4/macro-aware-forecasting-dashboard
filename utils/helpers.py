import os
import json
import pandas as pd
from datetime import datetime
from models.ensemble import generate_ensemble_signal
from utils.common import fetch_price_data

def load_config(config_path='forecast_config.json'):
    with open(config_path, 'r') as f:
        return json.load(f)

def scan_tickers(tickers, start_date, end_date, config):
    forecast_days = config.get('forecast_days', 5)
    signals = []

    for ticker in tickers:
        print(f"🔍 Scanning {ticker}...")
        try:
            data = fetch_price_data(ticker, start_date, end_date)

            result = generate_ensemble_signal(
                ticker=ticker,
                data=data,
                start_date=start_date,
                end_date=end_date,
                forecast_days=forecast_days,
                config=config
            )

            if result:
                signals.append(result)

        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")

    return pd.DataFrame(signals)

def save_signals_to_csv(df, filepath='data/top_trades.csv'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"💾 Saved results to {filepath}")
