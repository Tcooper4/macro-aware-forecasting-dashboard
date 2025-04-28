import streamlit as st
import pandas as pd
import yfinance as yf
# from forecast_engine import fetch_macro_data, detect_macro_regime  # 🚫 Commented out because not ready
from utils import navigation_bar

st.set_page_config(page_title="Macro Dashboard", layout="wide")
navigation_bar()

st.title("📈 Macro Dashboard")

with st.expander("ℹ️ About the Macro Dashboard", expanded=True):
    st.markdown("""
    This section helps you **analyze key macroeconomic indicators** and understand the current market environment.

    - 🏦 **Macro Indicators:** View trends for Inflation (CPI), Unemployment, Fed Funds Rate, and Real GDP.
    - 📈 **Visualization:** Interactive line charts of economic data over time.
    - 🧠 **Macro Regime Detection:** Automatically analyzes data to detect whether we are in Growth, Recession, or Stagflation.
    - 🎯 **Strategy Tips:** Get suggested investment strategies based on the detected regime.

    **Use this dashboard to align your investment decisions with the broader economic environment.**
    """)

st.markdown("### Analyze key macroeconomic indicators and detect market regimes.")

# --- Macroeconomic Indicators Setup ---
macro_options = {
    "CPIAUCSL": "Consumer Price Index (CPI)",
    "UNRATE": "Unemployment Rate",
    "FEDFUNDS": "Federal Funds Rate",
    "GDPC1": "Real GDP"
}

selected_indicators = st.multiselect(
    "Select macro indicators to visualize:",
    options=list(macro_options.keys()),
    default=["CPIAUCSL", "UNRATE", "FEDFUNDS"]
)

# 🚫 Temporarily comment out fetching macro data functionality
# if st.button("Load Macro Data"):
#     with st.spinner("Fetching macro data..."):
#         data = fetch_macro_data(selected_indicators)
#         if data is not None:
#             st.success("✅ Data Loaded Successfully!")
#             for code in selected_indicators:
#                 chart_title = f"📈 {macro_options.get(code, code)} Trend"
#                 st.subheader(chart_title)
#                 st.line_chart(data[code].rename(macro_options.get(code, code)))
#         else:
#             st.error("Failed to fetch macro data.")

# --- Detect Market Regime ---
st.subheader("🧠 Detect Current Macro Regime")

# 🚫 Temporarily comment out regime detection
# if st.button("Analyze Current Regime"):
#     regime, strategy = detect_macro_regime()
#     st.markdown(f"### 📊 Current Detected Regime: **{regime}**")
#     st.markdown(f"### 💼 Suggested Strategy: **{strategy}**")

# --- Put/Call Ratio Section ---
st.header("📊 Put/Call Ratio (Options Market Sentiment)")

@st.cache_data
def get_put_call_data():
    put_call = yf.download('^CPCE', period='1y', interval='1d', progress=False)
    put_call = put_call['Close'].dropna()
    return put_call

put_call_data = get_put_call_data()

st.line_chart(put_call_data)

if not put_call_data.empty:
    current_pc = float(put_call_data.iloc[-1])

    st.subheader("Current Put/Call Sentiment:")

    if current_pc > 1.0:
        st.success(f"🚀 High Fear: Put/Call Ratio = {current_pc:.2f} (Contrarian Buy Signal)")
    elif current_pc < 0.7:
        st.error(f"🛑 High Greed: Put/Call Ratio = {current_pc:.2f} (Caution Warranted)")
    else:
        st.info(f"😐 Neutral Sentiment: Put/Call Ratio = {current_pc:.2f}")
else:
    st.error("⚠️ Failed to load Put/Call Ratio data. Please try again later.")

