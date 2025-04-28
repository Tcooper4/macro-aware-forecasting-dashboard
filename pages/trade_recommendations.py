import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from forecast_engine import forecast_prices
from utils import navigation_bar

st.set_page_config(page_title="Trade Recommendations", layout="wide")
st.session_state["_page_"] = __file__
navigation_bar()

st.title("🛒 Daily Trade Recommendations")
st.markdown("### Generate trade ideas based on short-term forecasts with confidence intervals and risk analysis.")

# --- User Inputs ---
tickers_input = st.text_input("Enter stock tickers (comma-separated)", "AAPL, MSFT, SPY")
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
forecast_days = st.slider("Forecast Days Ahead", min_value=1, max_value=30, value=5)

tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

if st.button("Generate Forecasts"):
    with st.spinner("Fetching data and generating forecasts..."):
        forecast_results = {}
        risk_scores = {}
        for ticker in tickers:
            try:
                data = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
                if data.empty or data['Close'].dropna().empty:
                    st.warning(f"No valid price data for {ticker}. Skipping.")
                    continue

                forecast = forecast_prices(data['Close'].dropna(), forecast_days)

                vol = np.std(data['Close'].pct_change().dropna()) * np.sqrt(252)  # Annualized volatility
                risk = "Low" if vol < 0.2 else "Medium" if vol < 0.4 else "High"
                forecast_results[ticker] = forecast
                risk_scores[ticker] = risk
            except Exception as e:
                st.error(f"Failed to forecast {ticker}: {e}")

        if forecast_results:
            st.success("✅ Forecasts generated!")
            trade_recs = []

            for ticker, forecast in forecast_results.items():
                st.subheader(f"📈 {ticker} Forecast")
                forecast_df = pd.DataFrame({
                    "Forecast": forecast,
                    "Upper Bound": forecast * 1.05,
                    "Lower Bound": forecast * 0.95
                })
                st.line_chart(forecast_df)

                change_pct = (forecast[-1] - forecast[0]) / forecast[0]
                if change_pct > 0.02:
                    rec = "📈 Buy"
                    option_suggestion = "💬 Suggestion: Buy a Call Option"
                elif change_pct < -0.02:
                    rec = "📉 Sell"
                    option_suggestion = "💬 Suggestion: Buy a Put Option"
                else:
                    rec = "🤔 Hold"
                    option_suggestion = ""

                st.metric("Predicted Change (%)", f"{change_pct:.2%}")
                st.write(option_suggestion)

                trade_recs.append((ticker, rec, f"{change_pct:.2%}", risk_scores[ticker]))

            rec_df = pd.DataFrame(trade_recs, columns=["Ticker", "Recommendation", "Predicted % Change", "Risk Level"])

            # --- Filter Buttons ---
            filter_option = st.radio("Filter Recommendations", ("All", "📈 Buy", "📉 Sell", "🤔 Hold"))

            if filter_option != "All":
                rec_df = rec_df[rec_df["Recommendation"] == filter_option]

            # --- Top 3 Picks ---
            if not rec_df.empty:
                st.header("🏆 Top 3 Picks")
                top_picks = rec_df.copy()
                top_picks["% Change Numeric"] = top_picks["Predicted % Change"].str.replace("%", "").astype(float)
                top_picks = top_picks.sort_values("% Change Numeric", ascending=False).head(3)
                st.dataframe(top_picks.drop(columns=["% Change Numeric"]))

            # --- Full Table ---
            st.header("🔍 Trade Recommendation Summary")
            st.dataframe(rec_df)

            # --- Downloadable CSV ---
            csv = rec_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Recommendations as CSV",
                data=csv,
                file_name='trade_recommendations.csv',
                mime='text/csv',
            )

        else:
            st.error("No valid forecasts to display.")
