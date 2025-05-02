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

st.title("📊 Portfolio Optimization Dashboard")
st.caption("Optimize your asset allocation for maximum Sharpe Ratio using real market data.")

# Sidebar
tickers_input = st.sidebar.text_input("Enter tickers (comma-separated)", value="AAPL, MSFT, GOOG, AMZN")
start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
rf = st.sidebar.number_input("Risk-Free Rate (%)", 0.0, 10.0, 1.5) / 100

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
if len(tickers) < 2:
    st.warning("⚠️ Please enter at least two tickers.")
    st.stop()

@st.cache_data(ttl=3600)
def load_prices(tickers, start, end):
    data = {}
    for t in tickers:
        try:
            df = fetch_price_data(t, start, end)
            data[t] = df["Close"]
        except Exception as e:
            st.warning(f"{t} skipped: {e}")
    return pd.DataFrame(data)

prices = load_prices(tickers, start_date, end_date)
if prices.shape[1] < 2:
    st.error("Not enough valid data.")
    st.stop()

returns = prices.pct_change().dropna()

def neg_sharpe(weights, ret, rf):
    mean_ret = np.sum(weights * ret.mean()) * 252
    vol = np.sqrt(np.dot(weights.T, np.dot(ret.cov() * 252, weights)))
    return -(mean_ret - rf) / vol

n = len(tickers)
init = np.ones(n) / n
bounds = [(0, 1)] * n
constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

opt = minimize(neg_sharpe, init, args=(returns, rf), method="SLSQP", bounds=bounds, constraints=constraints)

if opt.success:
    w = pd.Series(opt.x, index=tickers)
    st.subheader("📈 Optimal Weights")
    st.bar_chart(w)

    ann_ret = np.sum(w * returns.mean()) * 252
    vol = np.sqrt(np.dot(w.T, np.dot(returns.cov() * 252, w)))
    sharpe = (ann_ret - rf) / vol
    port_ret = (returns * w).sum(axis=1)

    st.markdown(f"**Expected Return:** `{ann_ret:.2%}`")
    st.markdown(f"**Volatility:** `{vol:.2%}`")
    st.markdown(f"**Sharpe Ratio:** `{sharpe:.2f}`")

    cumret = (1 + port_ret).cumprod()
    maxdd = (cumret / cumret.cummax() - 1).min()
    st.markdown(f"**Max Drawdown:** `{maxdd:.2%}`")

    st.subheader("📉 Correlation Matrix")
    fig, ax = plt.subplots()
    sns.heatmap(returns.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    st.download_button("📥 Export Weights", w.reset_index().rename(columns={0: "Weight"}).to_csv(index=False).encode("utf-8"), "weights.csv")

else:
    st.error("❌ Optimization failed.")
