from dotenv import load_dotenv
import os

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

import streamlit as st
import pandas as pd
from datetime import datetime

from features.merge_data import merge_data
from fred_macro_data import fetch_and_plot_cached, get_macro_indicators

# Set the page configuration
st.set_page_config(page_title="Macro-Aware Forecasting Dashboard", layout="wide", page_icon="📈")

import streamlit as st

# --- Add Sidebar Navigation ---
with st.sidebar:
    st.header("🧭 Navigation")
    st.page_link("pages/portfolio_dashboard.py", label="💼 Portfolio Dashboard")
    st.page_link("pages/portfolio_optimization_dashboard.py", label="📊 Optimization Dashboard")
    st.page_link("pages/live_macro_charts.py", label="🌐 Macroeconomic Charts")

# Title and last updated time
st.title("📈 Macro-Aware Quant Forecasting Dashboard")
with st.expander("ℹ️ How This Platform Works", expanded=True):
    st.markdown("""
    This dashboard helps you:
    - 📈 Analyze market and macroeconomic trends.
    - 🛒 Get daily trade recommendations based on forecasts.
    - 📊 Optimize your stock portfolio to maximize returns.

    **Use the sidebar to navigate between tools!**
    """)

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")

# --- Sidebar Inputs ---
ticker = st.text_input("Enter a ticker symbol (e.g., SPY, AAPL):", value="SPY")
st.sidebar.title("📚 Instructions")

st.sidebar.markdown("""
- **Enter a stock ticker** (e.g., AAPL, SPY) to fetch stock data.
- **Load Data** to view historical prices.
- **Macro Dashboard:** Explore macroeconomic indicators.
- **Trade Recommendations:** Generate buy/sell trade ideas.
- **Portfolio Optimizer:** Optimize your investment portfolio.
""")

@st.cache_data
def merge_data_cached(ticker):
    return merge_data(ticker)

# --- Load Stock and Macro Data ---
if st.button("📥 Load Data"):
    with st.spinner("Fetching stock and macro data..."):
        df = merge_data_cached(ticker)
    st.success("✅ Data Loaded Successfully!")
    st.subheader(f"📊 Price Trend for {ticker}")
    st.line_chart(df[f"{ticker}_Close"])

# --- Macroeconomic Indicators Section ---
if st.sidebar.checkbox("Show Macroeconomic Indicators"):
    st.subheader("📊 Macroeconomic Trends")

    macro_options = {
        "CPIAUCSL": "Consumer Price Index (CPI)",
        "UNRATE": "Unemployment Rate",
        "FEDFUNDS": "Federal Funds Rate",
        "GDPC1": "Real GDP"
    }

    for code, label in macro_options.items():
        data = fetch_and_plot_cached(code, label)
        if data is not None:
            st.subheader(f"📉 {label}")
            st.line_chart(data.rename(columns={data.columns[0]: label}))

# --- Strategy Recommendation Section ---
if st.sidebar.checkbox("Show Strategy Recommendation"):
    st.subheader("🧠 Macro Regime Detection and Strategy Recommendation")

    df_macro = get_macro_indicators()
    if df_macro is not None and not df_macro.empty:
        st.dataframe(df_macro.tail(12), use_container_width=True)
        st.markdown("""
        Use macro patterns to interpret economic conditions and adjust your trading strategy:
        - 📈 **Growth Regime**: Favor stocks and risk-on assets.
        - 📉 **Recession**: Consider bonds or defensive sectors.
        - ⚖️ **Stagflation**: Prioritize inflation hedges (commodities, value stocks).
        """)
