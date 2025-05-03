import os
import pandas as pd
from utils.sp500_tickers import get_sp500_tickers
from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble
from features.strategy_engine import apply_strategy_settings
from pages.strategy_settings import get_user_strategy_settings

def scan_sp500_for_trades(horizon="1 Week", top_n=10):
    os.makedirs("data", exist_ok=True)

    tickers = get_sp500_tickers()[:10]  # Small set for debugging
    results = []

    for symbol in tickers:
        try:
            print(f"\n📈 Scanning {symbol}...")

            df = fetch_price_data(symbol)
            if df is None or df.empty:
                print(f"⚠️ No data for {symbol}. Skipping.")
                continue

            print(f"✅ Data fetched for {symbol}. Rows: {len(df)}")

            forecast = generate_forecast_ensemble(df, horizon)
            if not forecast or "forecast_table" not in forecast or "final_signal" not in forecast:
                print(f"⚠️ Forecast missing keys for {symbol}: {forecast}")
                continue

            forecast_df = forecast["forecast_table"]
            signal = forecast["final_signal"]
            rationale = forecast.get("rationale", "No rationale provided")

            print(f"🔎 {symbol} Signal: {signal}, Rationale: {rationale}")

            forecast_df["Final Signal"] = [signal] * len(forecast_df)

            try:
                strategy = apply_strategy_settings(forecast_df, get_user_strategy_settings())
            except Exception as se:
                print(f"⚠️ Strategy settings failed: {se}")
                strategy = {"action": "HOLD", "position_size": 0}

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
        print("⚠️ No valid trade signals found. Writing empty file.")
        pd.DataFrame(columns=["Ticker", "Signal", "Rationale", "Action", "Size", "Regime", "Confidence"]).to_csv("data/top_trades.csv", index=False)
