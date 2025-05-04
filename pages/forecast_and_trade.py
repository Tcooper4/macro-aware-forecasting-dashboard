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
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
forecast_horizon = st.sidebar.selectbox("Forecast Horizon", ["1 Day", "1 Week", "1 Month"], index=1)

user_strategy = get_user_strategy_settings()

# --- Load Data ---
try:
    df = fetch_price_data(ticker, start=start_date, end=end_date)
    st.success(f"✅ Loaded {ticker} data successfully.")
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
