import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="Forecast & Trade", layout="wide")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble, classify_market_regime
from pages.strategy_settings import get_user_strategy_settings
from features.strategy_engine import apply_strategy_settings

# --- Page Title ---
st.title("📈 Forecast & Trade Dashboard")

# --- Sidebar Inputs ---
ticker = st.sidebar.text_input("Enter Ticker", "AAPL").upper()
interval = st.sidebar.selectbox("Data Interval", ["1m", "5m", "15m", "30m", "60m", "1d"], index=2)
period = st.sidebar.selectbox("Lookback Period", ["1d", "5d", "7d", "1mo", "3mo", "6mo", "1y"], index=2)
forecast_horizon = st.sidebar.selectbox("Forecast Horizon", ["1 Day", "1 Week", "1 Month"], index=1)

user_strategy = get_user_strategy_settings()

# --- Load Data ---
try:
    df = fetch_price_data(ticker, interval=interval, period=period)
    if df.empty:
        raise ValueError("No data returned.")

    last_timestamp = df.index[-1]
    last_time_str = last_timestamp.strftime("%Y-%m-%d %H:%M")

    st.success(f"✅ Loaded {ticker} data successfully. Last updated: `{last_time_str}`")

    if pd.Timestamp.now(tz=last_timestamp.tz) - last_timestamp > pd.Timedelta("1D"):
        st.warning("⚠️ Data may be outdated. The market may be closed or the API is delayed.")

except Exception as e:
    st.error(f"❌ Failed to load data for {ticker}: {e}")
    st.stop()

# --- Generate Forecasts ---
st.subheader("🔮 Forecast Model Ensemble")
with st.spinner("Running forecasting models..."):
    results = generate_forecast_ensemble(df, horizon=forecast_horizon)
    forecast_df = results["forecast_table"]
    signal = str(results["final_signal"])
    rationale = str(results["rationale"])
    confidence_scores = results.get("model_confidences", {})

    st.dataframe(forecast_df.tail(10), use_container_width=True)

# --- Market Regime Detection ---
regime = classify_market_regime(df)

st.subheader("🧭 Detected Market Regime")
st.markdown(f"**Current Market Regime:** `{regime}`")

# --- Final Signal Display ---
st.subheader("📌 Final Trade Signal")
st.markdown(f"### 📍 **Signal: `{signal}`**")
st.markdown(f"🧠 **Rationale:** {rationale}")

# --- Confidence Scores ---
if confidence_scores:
    st.markdown("### 📊 Model Confidence Scores:")
    for model, score in confidence_scores.items():
        try:
            st.markdown(f"- **{model}:** {float(score):.2%}")
        except:
            st.markdown(f"- **{model}:** N/A")

# --- Strategy-Based Recommendation ---
forecast_df["Final Signal"] = [signal] * len(forecast_df)
strategy_output = apply_strategy_settings(forecast_df, user_strategy)

st.subheader("🛠️ Strategy-Based Trade Recommendation")
st.write(f"**Suggested Action:** `{strategy_output['action']}`")
st.write(f"**Position Size:** `{strategy_output['position_size']}%` — Use this percentage of your portfolio.")
st.write(f"**Trade Frequency:** `{strategy_output['frequency']}` — Re-evaluate or re-enter on this schedule.")

# --- Option Trade Details (Basic Calculation) ---
last_price = df["Close"].iloc[-1]
avg_conf = sum([
    v for v in confidence_scores.values()
    if isinstance(v, (int, float)) and v > 0
]) / max(1, len([v for v in confidence_scores.values() if isinstance(v, (int, float)) and v > 0]))

forecast_return = avg_conf
forecast_price = round(last_price * (1 + forecast_return), 2)
strike_price = round(forecast_price * 1.01, 2) if signal == "BUY" else round(forecast_price * 0.99, 2)
option_type = "CALL" if signal == "BUY" else "PUT"

st.subheader("💡 Trade Execution Details")
st.markdown(f"""
- **Current Price:** ${last_price:.2f}
- **Forecast Price:** ${forecast_price:.2f}
- **Suggested Option Type:** `{option_type}`
- **Suggested Strike Price:** `${strike_price}`
- **Estimated Expiration Date:** `{pd.Timestamp.now().normalize() + pd.Timedelta('21D'):%B %d, %Y}`
""")

# --- Forecast Chart with Overlay ---
st.subheader("📈 Price Chart with Forecast Overlay")

forecast_days = {
    "1 Day": 1,
    "1 Week": 5,
    "1 Month": 21
}.get(forecast_horizon, 5)

price_trace = go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Historical Price")

try:
    if forecast_days > 1:
        forecast_dates = [df.index[-1] + timedelta(days=i+1) for i in range(forecast_days)]
        forecast_prices = [forecast_price for _ in forecast_dates]
        forecast_trace = go.Scatter(x=forecast_dates, y=forecast_prices, mode="lines+markers", name="Forecast")
    else:
        forecast_trace = go.Scatter(
            x=[df.index[-1] + timedelta(days=1)],
            y=[forecast_price],
            mode="markers",
            marker=dict(size=10, color="orange"),
            name="Forecast (Next Day)"
        )

    strike_line = go.Scatter(
        x=[df.index[-1], df.index[-1] + timedelta(days=forecast_days)],
        y=[strike_price] * 2,
        mode="lines",
        line=dict(dash="dash", color="red"),
        name=f"Strike Price (${strike_price})"
    )

    st.plotly_chart(go.Figure(data=[price_trace, forecast_trace, strike_line]), use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Could not plot forecast overlay: {e}")
    st.plotly_chart(go.Figure(data=[price_trace]), use_container_width=True)

# --- CSV Export ---
csv = forecast_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Forecast CSV", csv, f"{ticker}_forecast.csv", "text/csv")

# --- Beginner-Friendly Regime Explanation ---
with st.expander("📘 What does this regime mean?"):
    st.markdown(f"""
    ### Market Regime: **{regime}**
    - **Bull:** Strong, upward-trending markets. Favor long positions.
    - **Bear:** Weak or declining markets. Reduce risk or consider short strategies.
    - **Neutral:** Sideways or uncertain markets. Maintain balanced exposure.
    
    The final signal above has been adjusted with this regime in mind to improve accuracy.
    """)
