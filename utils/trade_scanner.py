import os
import pandas as pd
from utils.sp500_tickers import get_sp500_tickers
from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble
from features.strategy_engine import apply_strategy_settings
from pages.strategy_settings import get_user_strategy_settings

def scan_sp500_for_trades(horizon="1 Week", top_n=10):
    os.makedirs("data", exist_ok=True)

    # TEMP: Limit to 10 tickers for faster debugging
    tickers = get_sp500_tickers()[:10]
    results = []

    for symbol in tickers:
        try:
            print(f"📈 Scanning {symbol}...")

            df = fetch_price_data(symbol)
            print(f"✅ Data fetched for {symbol}. Rows: {len(df)}")

            forecast = generate_forecast_ensemble(df, horizon)
            print(f"🧠 Forecast output for {symbol}: {forecast}")

            forecast_df = forecast["forecast_table"]
            signal = forecast["final_signal"]
            rationale = forecast["rationale"]

            forecast_df["Final Signal"] = [signal] * len(forecast_df)
            strategy_settings = get_user_strategy_settings()
            strategy = apply_strategy_settings(forecast_df, strategy_settings)

            print(f"🔎 {symbol} → Signal: {signal}")

            # TEMP: Include all non-null signals for testing, not just BUY/SELL
            if signal:
                print(f"✅ Adding {symbol} to results")
                results.append({
                    "Ticker": symbol,
                    "Signal": signal,
                    "Rationale": rationale,
                    "Action": strategy["action"],
                    "Size": strategy["position_size"],
                    "Regime": forecast.get("regime", "Unknown"),
                    "Confidence": abs(forecast_df["Average"].iloc[-1] / df["Close"].iloc[-1] - 1)
                })

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            continue

    df_results = pd.DataFrame(results)

    if not df_results.empty:
        df_results = df_results.sort_values(by="Confidence", ascending=False).head(top_n)
        df_results.to_csv("data/top_trades.csv", index=False)
        print("✅ Saved top trades to data/top_trades.csv")
    else:
        print("⚠️ No valid trade signals found. Writing empty placeholder file.")
        pd.DataFrame(columns=["Ticker", "Signal", "Rationale", "Action", "Size", "Regime", "Confidence"]).to_csv("data/top_trades.csv", index=False)
