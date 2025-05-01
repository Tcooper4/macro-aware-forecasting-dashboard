import streamlit as st
import pandas as pd
from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble

st.set_page_config(page_title="Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Suggestions")

# Sidebar
ticker = st.sidebar.text_input("Enter Ticker", "AAPL").upper()
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
forecast_horizon = st.sidebar.selectbox("Forecast Horizon", ["1 Day", "1 Week", "1 Month"], index=1)

# Load data
try:
    df = fetch_price_data(ticker, start_date, end_date)
    st.success(f"Loaded {ticker} data.")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Show price chart
st.line_chart(df["Close"])

# Forecasting
st.subheader("📊 Model Forecast Ensemble")
with st.spinner("Running forecasts..."):
    results = generate_forecast_ensemble(df, horizon=forecast_horizon)

    st.dataframe(results["forecast_table"].tail(10))

    st.subheader("📌 Final Trade Signal")
    signal = results["final_signal"]
    st.markdown(f"### 📍 **Signal: {signal}**")
    st.markdown(results["rationale"])

# Export
csv = results["forecast_table"].to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Forecast CSV", csv, f"{ticker}_forecast.csv", "text/csv")
