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

# --- Put/Call Ratio Section ---
st.header("📊 Put/Call Ratio (Options Market Sentiment) — Live Barchart.com Data")

@st.cache_data
def get_barchart_put_call():
    url = "https://www.barchart.com/stocks/most-active/put-call-ratios"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # This will find the first instance of put/call ratio
    try:
        table = soup.find('table')
        df = pd.read_html(str(table))[0]
        
        # Typically the first row is Index/Overall market, adjust if necessary
        equity_put_call = df.iloc[0]['Put/Call Ratio']
        return float(equity_put_call)
    except Exception as e:
        return None

put_call_value = get_barchart_put_call()

if put_call_value is not None:
    st.metric(label="Real-Time Put/Call Ratio (from Barchart)", value=f"{put_call_value:.2f}")

    st.subheader("Current Put/Call Sentiment:")

    if put_call_value > 1.0:
        st.success(f"🚀 High Fear: Put/Call Ratio = {put_call_value:.2f} (Contrarian Buy Signal)")
    elif put_call_value < 0.7:
        st.error(f"🛑 High Greed: Put/Call Ratio = {put_call_value:.2f} (Caution Warranted)")
    else:
        st.info(f"😐 Neutral Sentiment: Put/Call Ratio = {put_call_value:.2f}")
else:
    st.error("⚠️ Failed to fetch Put/Call Ratio. Please try again later.")
