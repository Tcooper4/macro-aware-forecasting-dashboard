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
from models.ensemble import classify_market_regime

st.title("📊 Portfolio Optimization (Regime-Aware + Sector-Tuned)")

# --- Sidebar Inputs ---
tickers_input = st.sidebar.text_input("Enter tickers (comma-separated)", value="AAPL, MSFT, XLF, TLT")
start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
rf = st.sidebar.number_input("Risk-Free Rate (%)", 0.0, 10.0, 1.5) / 100
regime_logic_enabled = st.sidebar.checkbox("Enable Regime-Switching Allocation", value=True)

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
if len(tickers) < 2:
    st.warning("⚠️ Please enter at least two tickers.")
    st.stop()

# --- Sector Tagging ---
st.sidebar.markdown("### 🏷️ Assign Sectors to Tickers")
sector_map = {}
for ticker in tickers:
    sector = st.sidebar.selectbox(f"{ticker} Sector", [
        "Technology", "Financials", "Healthcare", "Utilities", "Consumer Staples", "Energy", "Other"
    ], key=f"{ticker}_sector")
    sector_map[ticker] = sector

# --- Load price data ---
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
    st.error("❌ Not enough data to optimize.")
    st.stop()

returns = prices.pct_change().dropna()

# --- Optimization ---
def neg_sharpe(weights, ret, rf):
    mean_ret = np.sum(weights * ret.mean()) * 252
    vol = np.sqrt(np.dot(weights.T, np.dot(ret.cov() * 252, weights)))
    return -(mean_ret - rf) / vol

n = len(tickers)
init = np.ones(n) / n
bounds = [(0, 1)] * n
constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

opt = minimize(neg_sharpe, init, args=(returns, rf), method="SLSQP", bounds=bounds, constraints=constraints)

if not opt.success:
    st.error("❌ Optimization failed.")
    st.stop()

weights = pd.Series(opt.x, index=tickers)
regime = classify_market_regime(prices)

st.subheader("🧭 Detected Market Regime")
st.markdown(f"**Current Regime:** `{regime}`")

# --- Regime-aware adjustment ---
adjusted_weights = weights.copy()
if regime_logic_enabled:
    st.info("⚙️ Regime-switching adjustment enabled based on sectors.")
    risky_sectors = ["Technology", "Financials", "Energy"]
    if regime == "Bear":
        st.warning("🐻 Bear regime: reducing risky sector exposure.")
        for ticker in tickers:
            if sector_map.get(ticker) in risky_sectors:
                adjusted_weights[ticker] *= 0.5
    elif regime == "Bull":
        st.success("🐂 Bull regime: boosting growth sector exposure.")
        for ticker in tickers:
            if sector_map.get(ticker) in risky_sectors:
                adjusted_weights[ticker] *= 1.2
    adjusted_weights /= adjusted_weights.sum()
else:
    st.info("🔁 Regime adjustment is disabled.")

# --- Metrics ---
w = adjusted_weights
ann_ret = np.sum(w * returns.mean()) * 252
vol = np.sqrt(np.dot(w.T, np.dot(returns.cov() * 252, w)))
sharpe = (ann_ret - rf) / vol
port_ret = (returns * w).sum(axis=1)

st.subheader("📈 Regime-Aware Optimized Allocation")
st.bar_chart(w)

st.markdown(f"**Expected Return:** `{ann_ret:.2%}`")
st.markdown(f"**Volatility:** `{vol:.2%}`")
st.markdown(f"**Sharpe Ratio:** `{sharpe:.2f}`")

cumret = (1 + port_ret).cumprod()
maxdd = (cumret / cumret.cummax() - 1).min()
st.markdown(f"**Max Drawdown:** `{maxdd:.2%}`")
st.line_chart(cumret.rename("Portfolio Value"))

st.subheader("📉 Asset Correlation Heatmap")
fig, ax = plt.subplots()
sns.heatmap(returns.corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# --- Export Weights ---
df_out = pd.DataFrame({
    "Ticker": w.index,
    "Weight": w.values,
    "Sector": [sector_map[t] for t in w.index]
})
st.download_button("📥 Download Allocation", df_out.to_csv(index=False).encode("utf-8"), "regime_weights.csv", "text/csv")

# --- Strategy Guide ---
st.markdown("---")
st.subheader("📘 Regime-Based Strategy Guide")

st.markdown("""
| **Regime** | **Recommended Overweights**       | **Recommended Underweights**       |
|------------|-----------------------------------|------------------------------------|
| **Bull**   | Technology, Small Caps, Financials| Bonds, Utilities                   |
| **Bear**   | Bonds, Gold, Consumer Staples     | Tech, Emerging Markets             |
| **Neutral**| Balanced Mix, Defensive Growth    | N/A                                |

🧠 **What is this?**
Market regimes shift over time. This guide shows which asset types tend to perform better or worse during each phase.

- Bull markets: Favor growth and equities.
- Bear markets: Favor defensive or income-generating assets.
- Neutral: Keep a diversified stance.
""")
