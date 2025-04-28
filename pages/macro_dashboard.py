import streamlit as st
import pandas as pd
import yfinance as yf
# from forecast_engine import fetch_macro_data, detect_macro_regime  # 🚫 Commented out because not ready
from utils import navigation_bar
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

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
st.header("📊 Put/Call Ratio (Options Market Sentiment) — Real CBOE Data")

@st.cache_data
def get_cboe_put_call_data():
    url = "https://www.cboe.com/us/options/market_statistics/daily/"
    response = requests.get(url)

    if response.status_code != 200:
        return None  # Fail gracefully if CBOE website is down

    # Parse all tables
    tables = pd.read_html(response.text)

    # The table we want is usually the one with "Equity Put/Call Ratio"
    target_table = None
    for table in tables:
        if "Equity" in table.columns[0] and "Put/Call" in table.columns[0]:
            target_table = table
            break

    if target_table is None:
        return None  # No matching table found

    # Clean the table
    target_table.columns = ['Metric', 'Today', 'Previous']
    target_table = target_table.set_index('Metric')

    equity_put_call_today = target_table.loc['Equity Option Put/Call Ratio', 'Today']

    return float(equity_put_call_today)

# --- Fetch real CBOE Put/Call Ratio ---
st.header("📊 Put/Call Ratio (Options Market Sentiment) — Real CBOE Data (via Selenium)")

@st.cache_data
def get_cboe_put_call_selenium():
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    
    # Load CBOE page
    url = "https://www.cboe.com/us/options/market_statistics/daily/"
    driver.get(url)

    # Let it load
    driver.implicitly_wait(10)

    # Get page source and parse
    soup = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    # Find the correct table
    tables = pd.read_html(str(soup))
    target_table = None
    for table in tables:
        if "Equity" in table.columns[0] and "Put/Call" in table.columns[0]:
            target_table = table
            break

    if target_table is None:
        return None

    target_table.columns = ['Metric', 'Today', 'Previous']
    target_table = target_table.set_index('Metric')

    equity_put_call_today = target_table.loc['Equity Option Put/Call Ratio', 'Today']

    return float(equity_put_call_today)

# --- Fetch real CBOE Put/Call Ratio ---
put_call_value = get_cboe_put_call_selenium()

if put_call_value is not None:
    st.metric(label="Real-Time Equity Put/Call Ratio", value=f"{put_call_value:.2f}")

    # Interpretation
    st.subheader("Current Put/Call Sentiment:")

    if put_call_value > 1.0:
        st.success(f"🚀 High Fear: Put/Call Ratio = {put_call_value:.2f} (Contrarian Buy Signal)")
    elif put_call_value < 0.7:
        st.error(f"🛑 High Greed: Put/Call Ratio = {put_call_value:.2f} (Caution Warranted)")
    else:
        st.info(f"😐 Neutral Sentiment: Put/Call Ratio = {put_call_value:.2f}")
else:
    st.error("⚠️ Failed to fetch Put/Call Ratio from CBOE. Please try again later.")