import streamlit as st
import pandas as pd

from features.merge_data import merge_data
from fred_macro_data import fetch_and_plot, get_macro_indicators

st.set_page_config(page_title="Macro-Aware Forecasting Dashboard", layout="wide")

st.title("📈 Macro-Aware Quant Forecasting Dashboard")

ticker = st.text_input("Enter a ticker symbol (e.g., SPY, AAPL):", value="SPY")

if st.button("Load Data"):
    with st.spinner("Fetching data..."):
        df = merge_data(ticker)
        st.success("Data Loaded Successfully!")
        st.line_chart(df[f"{ticker}_Close"])

if st.sidebar.checkbox("Show Macroeconomic Indicators"):
    st.subheader("📊 Macroeconomic Trends")
    macro_options = {
        "CPIAUCSL": "Consumer Price Index (CPI)",
        "UNRATE": "Unemployment Rate",
        "FEDFUNDS": "Federal Funds Rate",
        "GDPC1": "Real GDP"
    }
    for code, label in macro_options.items():
        data = fetch_and_plot(code, label)
        st.line_chart(data.rename(label))

if st.sidebar.checkbox("Show Strategy Recommendation"):
    df_macro = get_macro_indicators().resample('M').last().dropna().iloc[-1]

    cpi = df_macro['CPI']
    gdp = df_macro['Real GDP']
    unemp = df_macro['Unemployment Rate']
    fedrate = df_macro['Fed Funds Rate']

    if cpi > 300 and gdp < 20000:
        regime = "Stagflation"
        strategy = "Defensive: Bonds, Utilities, Low Volatility Stocks"
    elif gdp > 21000 and unemp < 4:
        regime = "Growth"
        strategy = "Aggressive: Tech, Consumer Discretionary"
    else:
        regime = "Neutral"
        strategy = "Balanced Allocation: SPY + Macro Hedge"

    st.markdown(f"### 🧠 Detected Macro Regime: **{regime}**")
    st.markdown(f"#### 💼 Suggested Strategy: {strategy}")
