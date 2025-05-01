import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble
from pages.strategy_settings import get_user_strategy_settings
from features.strategy_engine import apply_strategy_settings

st.set_page_config(page_title="Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Suggestions")

# Sidebar controls
ticker = st.sidebar.text_input("Enter Ticker", "AAPL").upper()
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
forecast_horizon = st.sidebar.selectbox("Forecast Horizon", ["1 Day", "1 Week", "1 Month"], index=1)

# Strategy settings (risk, frequency, size)
user_strategy = get_user_strategy_settings()

# Load and show price data
try:
    df = fetch_price_data(ticker, start_date, end_date)
    st.success(f"Loaded {ticker} data.")
    st.line_chart(df["Close"])
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Forecast + signal
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

# CSV Export
csv = forecast_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Forecast CSV", csv, f"{ticker}_forecast.csv", "text/csv")
