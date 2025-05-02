import streamlit as st
st.set_page_config(page_title="Portfolio Optimization", layout="wide")

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.helpers import fetch_price_data

st.title("📈 Portfolio Optimization Dashboard")
st.caption("Optimize your portfolio for maximum Sharpe Ratio using historical data.")

# Sidebar
tickers_input = st.sidebar.text_input("Enter stock tickers (comma-separated)", value="AAPL, MSFT, GOOG")
start_date = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
risk_free_rate = st.sidebar.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=10.0, value=1.5) / 100

# Parse tickers
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
if len(tickers) < 2:
    st.warning("⚠️ Please enter at least two stock tickers.")
    st.stop()

# Load price data
def get_combined_data(tickers, start, end):
    price_data = {}
    for t in tickers:
        try:
            df = fetch_price_data(t, start, end)
            price_data[t] = df["Close"]
        except Exception as e:
            st.warning(f"⚠️ Could not load data for {t}: {e}")
    return pd.DataFrame(price_data)

price_df = get_combined_data(tickers, start_date, end_date)
if price_df.empty or price_df.shape[1] < 2:
    st.error("❌ Not enough valid data to optimize portfolio.")
    st.stop()

# Compute returns
returns = price_df.pct_change().dropna()

# Sharpe ratio objective
def neg_sharpe(weights, returns, rf):
    port_return = np.sum(returns.mean() * weights) * 252
    port_std = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe = (port_return - rf) / port_std
    return -sharpe

# Optimization
n_assets = len(tickers)
init_guess = np.ones(n_assets) / n_assets
bounds = tuple((0, 1) for _ in range(n_assets))
constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

opt = minimize(neg_sharpe, init_guess, args=(returns, risk_free_rate),
               method='SLSQP', bounds=bounds, constraints=constraints)

# Output results
if opt.success:
    st.subheader("💼 Optimized Portfolio Allocation")
    weights = pd.Series(opt.x, index=tickers)
    st.bar_chart(weights)

    port_return = np.sum(returns.mean() * weights) * 252
    port_std = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe_ratio = (port_return - risk_free_rate) / port_std

    st.markdown(f"**Expected Annual Return:** {port_return:.2%}")
    st.markdown(f"**Expected Volatility:** {port_std:.2%}")
    st.markdown(f"**Sharpe Ratio:** {sharpe_ratio:.2f}")
else:
    st.error("❌ Optimization failed.")
