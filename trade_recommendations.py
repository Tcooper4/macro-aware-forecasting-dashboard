import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from forecast_engine import forecast_prices
from utils import navigation_bar

st.set_page_config(page_title="Trade Recommendations", layout="wide")
navigation_bar()

st.title("🛒 Daily Trade Recommendations")

st.markdown("### Generate trade ideas based on short-term forecasts.")

# --- User Inputs ---
tickers_input = st.text_input("Enter stock tickers (comma-separated)", "AAPL, MSFT, SPY")
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
forecast_days = st.slider("Forecast Days Ahead", min_value=1, max_value=30, value=5)

tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

if st.button("Generate Forecasts"):
    with st.spinner("Fetching data and generating forecasts..."):
        forecast_results = {}
        for ticker in tickers:
            try:
                data = yf.download(ticker, start=start_date, progress=False)
                if data.empty:
                    st.warning(f"No data found for {ticker}. Skipping.")
                    continue
                forecast = forecast_prices(data['Close'], forecast_days)
                forecast_results[ticker] = forecast
            except Exception as e:
                st.error(f"Failed to forecast {ticker}: {e}")

        if forecast_results:
            st.success("✅ Forecasts generated!")
            for ticker, forecast in forecast_results.items():
                st.subheader(f"📈 {ticker} Forecast")
                st.line_chart(forecast)
                st.metric("Predicted Change (%)", f"{(forecast[-1] - forecast[0]) / forecast[0]:.2%}")

            # Trade Recommendation Summary
            st.header("🔍 Trade Recommendation Summary")
            trade_recs = []
            for ticker, forecast in forecast_results.items():
                change_pct = (forecast[-1] - forecast[0]) / forecast[0]
                if change_pct > 0.02:
                    rec = "📈 Buy"
                elif change_pct < -0.02:
                    rec = "📉 Sell"
                else:
                    rec = "🤔 Hold"
                trade_recs.append((ticker, rec, f"{change_pct:.2%}"))

            rec_df = pd.DataFrame(trade_recs, columns=["Ticker", "Recommendation", "Predicted % Change"])
            st.dataframe(rec_df)
        else:
            st.error("No valid forecasts to display.")
