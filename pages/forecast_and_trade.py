import streamlit as st
st.set_page_config(page_title="Forecast & Trade", layout="wide")

import sys
import os
import pandas as pd

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
# --- Load Data ---
try:
    df = fetch_price_data(ticker, interval=interval, period=period)
    if df.empty:
        raise ValueError("No data returned.")

    # Get timestamp of last available data point
    last_timestamp = df.index[-1]
    last_time_str = last_timestamp.strftime("%Y-%m-%d %H:%M")

    # Display success + timestamp
    st.success(f"✅ Loaded {ticker} data successfully. Last updated: `{last_time_str}`")
    
    # Warn if data is not fresh (e.g., market closed)
    if pd.Timestamp.now(tz=last_timestamp.tz) - last_timestamp > pd.Timedelta("1D"):
        st.warning("⚠️ Data may be outdated. The market may be closed or the API is delayed.")

    # Show chart
    st.line_chart(df["Close"])
except Exception as e:
    st.error(f"❌ Failed to load data for {ticker}: {e}")
    st.stop()


# --- Generate Forecasts ---
st.subheader("🔮 Forecast Model Ensemble")
with st.spinner("Running forecasting models..."):
    results = generate_forecast_ensemble(df, horizon=forecast_horizon)
    forecast_df = results["forecast_table"]
    signal = results["final_signal"]
    rationale = results["rationale"]
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
        st.markdown(f"- **{model}:** {score:.2%}")

# --- Apply Strategy Settings ---
forecast_df["Final Signal"] = [signal] * len(forecast_df)
strategy_output = apply_strategy_settings(forecast_df, user_strategy)

st.subheader("🛠️ Strategy-Based Trade Recommendation")
st.write(f"**Suggested Action:** `{strategy_output['action']}`")
st.write(f"**Position Size:** `{strategy_output['position_size']}%`")
st.write(f"**Trade Frequency:** `{strategy_output['frequency']}`")

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
