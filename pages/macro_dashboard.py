import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
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
st.header("📊 Put/Call Ratio (Options Market Sentiment) — Live Data")

@st.cache_data
def get_marketwatch_put_call():
    url = "https://www.marketwatch.com/investing/index/cboe-equity-put-call-ratio"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        # Find the element containing the ratio
        price_span = soup.find("bg-quote", {"field": "Last"})

        if price_span:
            put_call_value = float(price_span.text.strip())
            return put_call_value
        else:
            return None
    except Exception as e:
        return None
    
    # --- Fetch and Display Put/Call Ratio ---
put_call_value = get_marketwatch_put_call()

if put_call_value is not None:
    st.metric(label="Real-Time Put/Call Ratio (from MarketWatch)", value=f"{put_call_value:.2f}")

    st.subheader("Current Put/Call Sentiment:")

    if put_call_value > 1.0:
        st.success(f"🚀 High Fear: Put/Call Ratio = {put_call_value:.2f} (Contrarian Buy Signal)")
    elif put_call_value < 0.7:
        st.error(f"🛑 High Greed: Put/Call Ratio = {put_call_value:.2f} (Caution Warranted)")
    else:
        st.info(f"😐 Neutral Sentiment: {put_call_value:.2f}")
else:
    st.error("⚠️ Failed to fetch Put/Call Ratio. Please try again later.")

