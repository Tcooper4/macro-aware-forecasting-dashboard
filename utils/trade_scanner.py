# trade_scanner.py

import os
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm

from sp500_tickers import get_sp500_tickers
from models.ensemble import generate_ensemble_signal

def scan_sp500_for_trades(horizon="1 Week", top_n=10):
    """
    Scans all S&P 500 tickers and generates ensemble-based trading signals.
    Saves top BUY signals with full model breakdown to CSV.
    """
    TICKERS = get_sp500_tickers()
    END_DATE = datetime.today().strftime('%Y-%m-%d')
    START_DATE = (datetime.today() - timedelta(days=3 * 365)).strftime('%Y-%m-%d')

    results = []

    for ticker in tqdm(TICKERS, desc="📈 Scanning S&P 500 Tickers"):
        try:
            signal_output = generate_ensemble_signal(
                ticker=ticker,
                start_date=START_DATE,
                end_date=END_DATE,
                settings={"horizon": horizon}
            )

            row = {
                "Ticker": ticker,
                "Final Signal": signal_output["final_signal"]
            }

            # Include model votes in the output
            for model_name, vote in signal_output["model_votes"].items():
                row[f"{model_name} Vote"] = vote

            results.append(row)

        except Exception as e:
            print(f"❌ Error on {ticker}: {e}")

    df = pd.DataFrame(results)

    # Filter to top BUY recommendations
    top_trades = df[df["Final Signal"] == "BUY"].head(top_n)

    os.makedirs("data", exist_ok=True)
    top_trades.to_csv("data/top_trades.csv", index=False)
    print("✅ Trade scan complete. Results saved to data/top_trades.csv")

if __name__ == "__main__":
    scan_sp500_for_trades(horizon="1 Week", top_n=10)
