import streamlit as st
st.set_page_config(page_title="Portfolio Overview", layout="wide")

import sys
import os
import pandas as pd
import numpy as np
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.helpers import fetch_price_data

st.title("📊 Portfolio Performance Overview")

# --- Sidebar Inputs ---
tickers_input = st.sidebar.text_input("Tickers (comma-separated)", "AAPL, MSFT, GOOG")
weights_input = st.sidebar.text_input("Weights (same order)", "0.4, 0.3, 0.3")
capital = st.sidebar.number_input("Initial Capital ($)", 1000.0, 1_000_000.0, 10_000.0, step=1000.0)
start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
weights = [float(w.strip()) for w in weights_input.split(",") if w.strip()]
if len(tickers) != len(weights):
    st.error("❌ Number of tickers must match number of weights.")
    st.stop()
if not np.isclose(sum(weights), 1.0):
    st.error("❌ Weights must sum to 1.0")
    st.stop()

# --- Load price data ---
@st.cache_data(ttl=3600)
def load_prices(tickers, start, end):
    price_data = {}
    for t in tickers:
        try:
            df = fetch_price_data(t, start, end)
            price_data[t] = df["Close"]
        except Exception as e:
            st.warning(f"{t} skipped: {e}")
    return pd.DataFrame(price_data)

prices = load_prices(tickers, start_date, end_date)
if prices.empty or prices.shape[1] < 2:
    st.error("❌ Not enough price data to compute portfolio overview.")
    st.stop()

# --- Calculate metrics ---
returns = prices.pct_change().dropna()
weights_arr = np.array(weights)
daily_returns = returns.dot(weights_arr)
cumulative = (1 + daily_returns).cumprod()
portfolio_value = cumulative * capital
drawdown = (portfolio_value / portfolio_value.cummax()) - 1

# Metrics
total_return = portfolio_value.iloc[-1] / capital - 1
volatility = daily_returns.std() * np.sqrt(252)
sharpe = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
max_dd = drawdown.min()

# --- Display ---
st.subheader("📈 Portfolio Value Over Time")
st.line_chart(portfolio_value)

st.subheader("📊 Performance Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Return", f"{total_return:.2%}")
col2.metric("Annual Volatility", f"{volatility:.2%}")
col3.metric("Sharpe Ratio", f"{sharpe:.2f}")

st.subheader("📉 Drawdown")
st.line_chart(drawdown)

# --- Download ---
df_export = pd.DataFrame({
    "Date": portfolio_value.index,
    "Portfolio Value": portfolio_value.values,
    "Daily Return": daily_returns.values,
    "Drawdown": drawdown.values
})
st.download_button("📥 Download CSV", df_export.to_csv(index=False).encode("utf-8"), "portfolio_overview.csv", "text/csv")
