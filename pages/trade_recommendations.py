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

            if data.empty or 'Close' not in data.columns:
                st.warning(f"No valid price data for {ticker}. Skipping.")
                continue

            # Force Clean Close Prices
            close_raw = data['Close'].dropna().astype(float)
            close_prices = pd.Series(close_raw.values.flatten(), index=close_raw.index)  # <-- Flatten added here

            # Hard sanity checks
            if close_prices.empty or len(close_prices) < 60:
                st.warning(f"Not enough clean price data for {ticker}. Skipping.")
                continue

            if not isinstance(close_prices, pd.Series):
                st.warning(f"Invalid data type for {ticker}. Skipping.")
                continue

            # Select model and forecast
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

            import plotly.graph_objects as go

            # Define history window
            history = close_prices[-60:]  # Last 60 days of real prices
            forecast_start_date = forecast.index[0]

            # Estimate confidence intervals (simple +/- 1.5% of forecast as example)
            upper_conf = forecast * 1.015
            lower_conf = forecast * 0.985

            fig = go.Figure()

            # Plot actual past prices
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history.values,
                mode='lines',
                name='Historical Prices',
                line=dict(color='blue')
            ))

            # Plot forecasted future prices
            fig.add_trace(go.Scatter(
                x=forecast.index,
                y=forecast.values,
                mode='lines',
                name='Forecasted Prices',
                line=dict(color='green', dash='dash')
            ))

            # Plot confidence intervals
            fig.add_trace(go.Scatter(
                x=list(forecast.index) + list(forecast.index[::-1]),
                y=list(upper_conf.values) + list(lower_conf.values[::-1]),
                fill='toself',
                fillcolor='rgba(0, 255, 0, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name='Confidence Interval'
            ))

            # Detect trend for annotation
            trend = forecast.iloc[-1] - forecast.iloc[0]

            if trend > 0:
                annotation_text = "BUY 📈"
                annotation_color = "green"
            else:
                annotation_text = "SELL 📉"
                annotation_color = "red"

            # Add annotation
            fig.add_trace(go.Scatter(
                x=[forecast.index[-1]],
                y=[forecast.iloc[-1]],
                mode='markers+text',
                marker=dict(color=annotation_color, size=12),
                text=[annotation_text],
                textposition="top center",
                showlegend=False
            ))

            fig.update_layout(
                title=f"Price Forecast for {ticker}",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                xaxis=dict(
                    range=[history.index.min(), forecast.index.max()],
                    showgrid=True
                ),
                yaxis=dict(
                    showgrid=True
                ),
                legend=dict(x=0, y=1),
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.info(f"**Risk Level:** {risk_scores[ticker]}")

        st.success("✅ Forecasts Generated Successfully!")
    else:
        st.warning("⚠️ No forecasts available. Please adjust your inputs or check ticker data.")
