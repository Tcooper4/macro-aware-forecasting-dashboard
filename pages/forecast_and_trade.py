import streamlit as st
st.set_page_config(page_title="Forecast & Trade", layout="wide")  # ✅ must be first

import sys
import os
import pandas as pd

# Add project root to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble
from pages.strategy_settings import get_user_strategy_settings
from features.strategy_engine import apply_strategy_settings

# App title
st.title("📈 Forecast & Trade Suggestions")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter Ticker", "AAPL").upper()
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
forecast_horizon = st.sidebar.selectbox("Forecast Horizon", ["1 Day", "1 Week", "1 Month"], index=1)

# Strategy config
user_strategy = get_user_strategy_settings()

# Load data
try:
    df = fetch_price_data(ticker, start=start_date, end=end_date)
    if df.empty:
        raise ValueError("Data returned was empty.")
    st.success(f"Loaded {ticker} data.")
    st.line_chart(df["Close"])
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Run forecast models
st.subheader("📊 Model Forecast Ensemble")
with st.spinner("Running models..."):
    results = generate_forecast_ensemble(df, horizon=forecast_horizon)
    forecast_df = results["forecast_table"]
    st.dataframe(forecast_df.tail(10))

    st.subheader("📌 Final Trade Signal")
    signal = results["final_signal"]
    rationale = results["rationale"]
    st.markdown(f"### 📍 **Signal: {signal}**")
    st.markdown(rationale)

# Strategy overlay
st.subheader("🛠️ Strategy Output")
strategy_output = apply_strategy_settings(forecast_df.assign(Final_Signal=signal), user_strategy)
st.write(f"💼 Suggested Action: **{strategy_output['action']}**")
st.write(f"📊 Position Size: **{strategy_output['position_size']}%** of portfolio")
st.write(f"🔁 Frequency: **{strategy_output['frequency']}**")

# Download forecast table
csv = forecast_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Forecast CSV", csv, f"{ticker}_forecast.csv", "text/csv")
