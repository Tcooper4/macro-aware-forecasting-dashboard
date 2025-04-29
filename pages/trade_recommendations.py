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
import plotly.graph_objects as go

st.set_page_config(page_title="Trade Recommendations", layout="wide")
navigation_bar()

st.title("🛒 Daily Trade Recommendations")

# Sidebar Instructions
st.sidebar.title("📚 Instructions")
st.sidebar.markdown("""
- **Enter stock tickers** (comma separated, e.g., AAPL, TSLA, MSFT).
- **Select a forecast model** (Simple → Elite).
- **Choose start date** for historical data.
- **Pick forecast horizon** (3-30 days).
""")

# --- User Inputs ---
st.header("🔎 Select Forecast Settings")

model_choice = st.selectbox(
    "Select Forecasting Model:",
    [
        "Simple - Exponential Smoothing",
        "Intermediate - ARIMA",
        "Advanced - Prophet",
        "Expert - SARIMA",
        "Elite - LSTM Neural Net",
        "Hybrid - ARIMA + Prophet"
    ]
)

tickers = st.text_input("Enter Stock Tickers (separated by commas)", value="AAPL,MSFT,TSLA")
start_date = st.date_input("Select Start Date", pd.to_datetime("2022-01-01"))
forecast_days = st.slider("Days to Forecast", 3, 30, 7)

st.markdown("---")

# --- Main Forecast Execution ---
if st.button("📈 Generate Forecasts"):
    tickers = [ticker.strip().upper() for ticker in tickers.split(",")]
    forecast_results = {}
    risk_scores = {}
    volatilities = {}

    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)

            if data.empty or 'Close' not in data.columns:
                st.warning(f"No valid price data for {ticker}. Skipping.")
                continue

            close_raw = data['Close'].dropna().astype(float)
            close_prices = pd.Series(close_raw.values.flatten(), index=close_raw.index)

            if close_prices.empty or len(close_prices) < 60:
                st.warning(f"Not enough clean price data for {ticker}. Skipping.")
                continue

            if not isinstance(close_prices, pd.Series):
                st.warning(f"Invalid data type for {ticker}. Skipping.")
                continue

            # Select Model
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
            elif model_choice == "Hybrid - ARIMA + Prophet":
                forecast1 = forecast_prices_arima(close_prices, forecast_days)
                forecast2 = forecast_prices_prophet(close_prices, forecast_days)
                forecast = (forecast1 + forecast2) / 2
            else:
                st.error("Invalid Model Choice.")
                continue

            vol = np.std(close_prices.pct_change().dropna()) * np.sqrt(252)
            risk = "Low" if vol < 0.2 else "Medium" if vol < 0.4 else "High"

            forecast_results[ticker] = forecast
            risk_scores[ticker] = risk
            volatilities[ticker] = vol

        except Exception as e:
            st.error(f"Failed to forecast {ticker}: {e}")

    st.markdown("---")

    if forecast_results:
        for ticker, forecast in forecast_results.items():
            st.subheader(f"📈 {ticker} — {forecast_days}-Day Price Forecast")

            upper_conf = forecast * 1.015
            lower_conf = forecast * 0.985
            history = close_prices[-60:].sort_index()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=history.index, y=history.values, mode='lines', name='Historical', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=forecast.index, y=forecast.values, mode='lines', name='Forecasted', line=dict(color='green', dash='dash')))
            fig.add_trace(go.Scatter(
                x=list(forecast.index) + list(forecast.index[::-1]),
                y=list(upper_conf.values) + list(lower_conf.values[::-1]),
                fill='toself',
                fillcolor='rgba(0,255,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name='Confidence Interval'
            ))

            trend = forecast.iloc[-1] - forecast.iloc[0]
            annotation_text = "BUY 📈" if trend > 0 else "SELL 🖉"
            annotation_color = "green" if trend > 0 else "red"

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
                title=f"{ticker} — {forecast_days}-Day Forecast",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                xaxis=dict(type='date', showgrid=True, rangeslider=dict(visible=True)),
                yaxis=dict(showgrid=True),
                legend=dict(x=0, y=1),
                template="plotly_white",
            )

            st.plotly_chart(fig, use_container_width=True)

            risk = risk_scores[ticker]
            vol = volatilities[ticker]
            risk_color = "🟢 Low" if risk == "Low" else "🟡 Medium" if risk == "Medium" else "🔴 High"

            expected_return = ((forecast.iloc[-1] / forecast.iloc[0]) - 1) * 100
            st.markdown(f"**Volatility:** {vol:.2%}  |  **Risk Level:** {risk_color}  |  **Expected Return:** {expected_return:.2f}%")

        st.success("✅ Forecasts Generated Successfully!")
    else:
        st.warning("⚠️ No forecasts available. Please adjust your inputs or check ticker data.")
