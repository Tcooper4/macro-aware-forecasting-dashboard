import streamlit as st
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

import pandas as pd
import numpy as np
import yfinance as yf
from forecast_engine import (
    forecast_prices_smoothing,
    forecast_prices_arima,
    forecast_prices_prophet,
    forecast_prices_sarima,
    forecast_prices_lstm
)
from utils import navigation_bar

st.set_page_config(page_title="Trade Recommendations", layout="wide")
st.title("🛒 Daily Trade Recommendations")

navigation_bar()

st.sidebar.title("📚 Instructions")
st.sidebar.markdown("""
- **Enter a stock ticker** (e.g., AAPL, SPY) to fetch stock data.
- **Select a forecast model** to use.
- **Load Data** to view historical prices.
- **Forecast future prices** and get trade ideas.
""")

# Model selection
model_choice = st.sidebar.selectbox(
    "Select Forecasting Model",
    [
        "Simple - Exponential Smoothing",
        "Intermediate - ARIMA",
        "Advanced - Prophet",
        "Expert - SARIMA",
        "Elite - LSTM Neural Net"
    ]
)

# User Inputs
tickers = st.text_input("Enter Stock Tickers (separated by commas)", value="AAPL,MSFT,TSLA")
start_date = st.date_input("Select Start Date", pd.to_datetime("2022-01-01"))
forecast_days = st.slider("Days to Forecast", 3, 30, 5)

if st.button("Generate Forecasts"):
    tickers = [ticker.strip().upper() for ticker in tickers.split(",")]
    forecast_results = {}
    risk_scores = {}

    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)

            # Validate clean 'Close' prices
            if data.empty or 'Close' not in data.columns:
                st.warning(f"No valid price data for {ticker}. Skipping.")
                continue

            close_prices = data['Close'].dropna().astype(float)

            # HARD SANITY CHECK
            if close_prices.empty or len(close_prices) < 60:
                st.warning(f"Not enough clean price data for {ticker}. Skipping.")
                continue

            if not isinstance(close_prices, pd.Series):
                st.warning(f"Invalid data type for {ticker}. Skipping.")
                continue

            # Route to selected model
            if model_choice == "Simple - Exponential Smoothing":
                forecast = forecast_prices_smoothing(close_prices, forecast_days)
            elif model_choice == "Intermediate - ARIMA":
                forecast = forecast_prices_arima(close_prices, forecast_days)
            elif model_choice == "Advanced - Prophet":
                forecast = forecast_prices_prophet(close_prices, forecast_days)
            elif model_choice == "Expert - SARIMA":
                forecast = forecast_prices_sarima(close_prices, forecast_days)
            elif model_choice == "Elite - LSTM Neural Net":
                forecast = forecast_prices_lstm(close_prices, forecast_days)
            else:
                st.error("Invalid Model Choice")
                continue

            vol = np.std(close_prices.pct_change().dropna()) * np.sqrt(252)
            risk = "Low" if vol < 0.2 else "Medium" if vol < 0.4 else "High"
            forecast_results[ticker] = forecast
            risk_scores[ticker] = risk

        except Exception as e:
            st.error(f"Failed to forecast {ticker}: {e}")


    # Display Results
    if forecast_results:
        for ticker, forecast in forecast_results.items():
            st.subheader(f"📈 Forecast for {ticker}")
            st.line_chart(forecast)

            trend = forecast.iloc[-1] - forecast.iloc[0]
            recommendation = "Buy" if trend > 0 else "Sell" if trend < 0 else "Hold"

            st.success(f"**Recommendation for {ticker}:** {recommendation}")
            st.info(f"**Risk Level:** {risk_scores[ticker]}")

        st.success("✅ Forecasts Generated Successfully!")
    else:
        st.warning("⚠️ No forecasts available. Please adjust your inputs or check ticker data.")
