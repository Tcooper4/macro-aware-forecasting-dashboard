# utils/trade_scanner.py

import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from tqdm import tqdm

from models.ensemble import generate_ensemble_signal


def scan_sp500_for_trades(horizon="1 Week", top_n=10):
    """
    Scans S&P 500 tickers and generates trading signals using ensemble modeling.

    Args:
        horizon (str): Time horizon for forecasts (e.g., "1 Week", "1 Month").
        top_n (int): Number of top trade recommendations to save.
    """
    TICKERS = [
        "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A"
    ]
    END_DATE = datetime.today().strftime('%Y-%m-%d')
    START_DATE = (datetime.today() - timedelta(days=3 * 365)).strftime('%Y-%m-%d')

    results = []

    for ticker in tqdm(TICKERS, desc="📈 Scanning tickers"):
        try:
            signal_output = generate_ensemble_signal(
                ticker=ticker,
                start_date=START_DATE,
                end_date=END_DATE,
                settings={"horizon": horizon}
            )
            results.append({
                "Ticker": ticker,
                **signal_output["model_votes"],
                "Final Signal": signal_output["final_signal"]
            })
        except Exception as e:
            print(f"❌ Error on {ticker}: {e}")

    df = pd.DataFrame(results)
    os.makedirs("data", exist_ok=True)
    top_trades = df[df["Final Signal"] == "BUY"].head(top_n)
    top_trades.to_csv("data/top_trades.csv", index=False)
    print("✅ Trade scan complete. Results saved to data/top_trades.csv")
