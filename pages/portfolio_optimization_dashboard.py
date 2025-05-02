import streamlit as st
st.set_page_config(page_title="Portfolio Optimization", layout="wide")

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.helpers import fetch_price_data

# --- Title ---
st.title("📊 Portfolio Optimization Dashboard")
st.caption("Optimize allocations to maximize Sharpe Ratio using live market data.")

# --- Sidebar Inputs ---
tickers_input = st.sidebar.text_input("Enter stock tickers (comma-separated)", value="AAPL, MSFT, GOOG, AMZN")
start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
risk_free_rate = st.sidebar.number_input("Risk-Free Rate (%)", 0.0, 10.0, 1.5) / 100

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
if len(tickers) < 2:
    st.warning("⚠️ Please enter at least two stock tickers.")
    st.stop()

# --- Fetch Price Data ---
@st.cache_data(ttl=3600)
def load_prices(tickers, start, end):
    price_data = {}
    for t in tickers:
        try:
            df = fetch_price_data(t, start, end)
            price_data[t] = df["Close"]
        except Exception as e:
            st.warning(f"⚠️ {t}: {e}")
    return pd.DataFrame(price_data)

prices = load_prices(tickers, start_date, end_date)
if prices.empty or prices.shape[1] < 2:
    st.error("❌ Not enough valid data to optimize.")
    st.stop()

# --- Calculate Returns ---
returns = prices.pct_change().dropna()

# --- Sharpe Optimization ---
def neg_sharpe(weights, ret, rf):
    port_ret = np.sum(weights * ret.mean()) * 252
    port_vol = np.sqrt(np.dot(weights.T, np.dot(ret.cov() * 252, weights)))
    sharpe = (port_ret - rf) / port_vol
    return -sharpe

# Constraints
n_assets = len(tickers)
init_guess = np.ones(n_assets) / n_assets
bounds = [(0.0, 1.0) for _ in range(n_assets)]
constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

# Run optimizer
opt = minimize(neg_sharpe, init_guess, args=(returns, risk_free_rate),
               method='SLSQP', bounds=bounds, constraints=constraints)

# --- Display Results ---
if opt.success:
    weights = pd.Series(opt.x, index=tickers)
    st.subheader("📈 Optimized Weights")
    st.bar_chart(weights)

    # Performance stats
    ann_return = np.sum(weights * returns.mean()) * 252
    ann_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe = (ann_return - risk_free_rate) / ann_vol

    st.markdown(f"**Expected Annual Return:** `{ann_return:.2%}`")
    st.markdown(f"**Expected Volatility:** `{ann_vol:.2%}`")
    st.markdown(f"**Sharpe Ratio:** `{sharpe:.2f}`")

    # Drawdown
    port_returns = (returns * weights).sum(axis=1)
    cum_returns = (1 + port_returns).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    st.markdown(f"**Max Drawdown:** `{drawdown.min():.2%}`")

    # --- Correlation Heatmap ---
    st.subheader("🔗 Asset Correlation")
    fig, ax = plt.subplots()
    sns.heatmap(returns.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # --- Export ---
    df_out = pd.DataFrame({
        "Ticker": tickers,
        "Weight": weights.values
    })
    st.download_button("📥 Download Weights", df_out.to_csv(index=False).encode("utf-8"),
                       "optimized_weights.csv", "text/csv")

else:
    st.error("❌ Optimization failed. Try different tickers or date range.")
