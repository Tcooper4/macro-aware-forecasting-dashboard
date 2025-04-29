import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")
st.title("💼 Portfolio Performance Dashboard")
st.caption("Analyze the historical performance and allocation of your portfolio.")

# --- Sidebar ---
st.sidebar.header("⚙️ Portfolio Settings")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated)", value="AAPL, MSFT, GOOG")
weights_input = st.sidebar.text_input("Enter portfolio weights (comma-separated)", value="0.4, 0.3, 0.3")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
freq = st.sidebar.selectbox("Return Frequency", ["Daily", "Weekly", "Monthly"])
st.sidebar.page_link("pages/portfolio_optimization_dashboard.py", label="📊 Go to Optimization Dashboard")

tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
weights = [float(w.strip()) for w in weights_input.split(",") if w.strip()]

if len(tickers) != len(weights):
    st.error("Number of tickers and weights must match.")
    st.stop()

# --- Fetch Data ---
@st.cache_data
def fetch_data(tickers, start, end):
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=True)['Close']
        if isinstance(data, pd.DataFrame) and not data.empty:
            return data
        else:
            return None
    except Exception:
        return None

df = fetch_data(tickers, start_date, end_date)

if df is None:
    st.error("Failed to fetch price data. Check ticker symbols and date range.")
    st.stop()

df = df.resample({'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}[freq]).last().dropna()
returns = df.pct_change().dropna()
weights = np.array(weights)
portfolio_returns = returns @ weights
cumulative = (1 + portfolio_returns).cumprod()
rolling_max = cumulative.cummax()
drawdown = (cumulative - rolling_max) / rolling_max
max_drawdown = drawdown.min()

# --- Portfolio Value Plot ---
with st.expander("📈 Portfolio Value Over Time", expanded=True):
    fig1, ax1 = plt.subplots()
    ax1.plot(cumulative, label='Portfolio Value')
    ax1.set_title("Portfolio Cumulative Return")
    ax1.set_ylabel("Value (Normalized)")
    ax1.legend()
    st.pyplot(fig1)

# --- Performance Metrics ---
with st.expander("📊 Key Performance Metrics"):
    st.metric("Total Return", f"{cumulative.iloc[-1] - 1:.2%}")
    st.metric("Annualized Volatility", f"{portfolio_returns.std() * np.sqrt(252):.2%}")
    st.metric("Max Drawdown", f"{max_drawdown:.2%}")
    st.metric("Mean Daily Return", f"{portfolio_returns.mean():.2%}")

# --- Daily PnL Chart ---
with st.expander("📉 Portfolio Daily Returns"):
    fig2, ax2 = plt.subplots()
    ax2.plot(portfolio_returns, color='orange')
    ax2.axhline(0, linestyle='--', linewidth=1, color='gray')
    ax2.set_title("Daily Portfolio Returns")
    st.pyplot(fig2)

# --- Allocation Pie Chart ---
with st.expander("🧮 Allocation Overview"):
    fig3, ax3 = plt.subplots()
    ax3.pie(weights, labels=tickers, autopct='%1.1f%%', startangle=90)
    ax3.axis('equal')
    st.pyplot(fig3)

# --- Downloadable Output ---
with st.expander("📥 Download Portfolio Data"):
    export_df = pd.DataFrame({
        "Date": cumulative.index,
        "Portfolio Value": cumulative.values,
        "Portfolio Return": portfolio_returns.values,
        "Drawdown": drawdown.values
    })
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="portfolio_performance.csv")
