import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Macro Sentiment Dashboard", page_icon="🌎", layout="wide")

st.title("🌎 Macro & Market Sentiment Dashboard")

# --- Section: VIX Fear Index ---
st.header("📈 VIX Fear Index (Market Volatility)")

@st.cache_data
def get_vix_data():
    vix = yf.download('^VIX', period='1y', interval='1d', progress=False)
    return vix['Close'].dropna()

vix_data = get_vix_data()

if vix_data.empty:
    st.error("⚠️ Failed to fetch VIX data.")
else:
    current_vix = float(vix_data.iloc[-1])
    st.line_chart(vix_data)

    if current_vix > 30:
        st.error(f"⚠️ High Volatility: VIX = {current_vix:.2f}")
    elif current_vix < 20:
        st.success(f"😊 Calm Market: VIX = {current_vix:.2f}")
    else:
        st.info(f"😐 Moderate Volatility: VIX = {current_vix:.2f}")

# --- Section: AAII Sentiment Placeholder ---
st.header("📊 AAII Investor Sentiment Survey")

st.info("Live AAII sentiment data support will be added soon. Currently disabled due to access limitations.")

st.markdown("""
While we finalize integration with the AAII data feed, this section will soon provide weekly sentiment breakdowns:

- 📈 **Bullish:** Investor optimism
- 😐 **Neutral:** Indecision or caution
- 📉 **Bearish:** Fear or risk-off attitude

Stay tuned for this upgrade to complete the macro sentiment dashboard!
""")
