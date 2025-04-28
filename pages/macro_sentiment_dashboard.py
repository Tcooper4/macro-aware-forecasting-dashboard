import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.set_page_config(page_title="Macro Sentiment Dashboard", page_icon="🌎", layout="wide")

st.title("🌎 Macro & Market Sentiment Dashboard")

# Fetch VIX Index
def get_vix_data():
    vix = yf.download('^VIX', period='1y', interval='1d', progress=False)
    vix = vix['Close'].dropna()
    return vix

# Section: VIX Fear Index
st.header("📈 VIX Fear Index (Market Volatility)")

vix_data = get_vix_data()
current_vix = float(vix_data.iloc[-1])

st.line_chart(vix_data)

if current_vix > 30:
    st.error(f"⚠️ High Volatility: VIX = {current_vix:.2f}")
elif current_vix < 20:
    st.success(f"😊 Calm Market: VIX = {current_vix:.2f}")
else:
    st.info(f"😐 Moderate Volatility: VIX = {current_vix:.2f}")

st.header("📊 AAII Investor Sentiment Survey")

@st.cache_data
def get_aaii_data():
    url = "https://www.aaii.com/sentimentsurvey"
    response = requests.get(url)
    dfs = pd.read_html(response.text)

    # AAII sentiment table is usually the first table on the page
    sentiment_table = dfs[0]

    # Clean column names
    sentiment_table.columns = ['Week Ended', 'Bullish', 'Neutral', 'Bearish']
    sentiment_table['Week Ended'] = pd.to_datetime(sentiment_table['Week Ended'])
    sentiment_table = sentiment_table.set_index('Week Ended')
    sentiment_table = sentiment_table.sort_index()

    return sentiment_table

# Fetch the AAII sentiment data
aaii_data = get_aaii_data()

# Line chart of sentiment
st.line_chart(aaii_data[['Bullish', 'Neutral', 'Bearish']])

# Latest values
latest_aaii = aaii_data.iloc[-1]

st.subheader("Latest AAII Readings:")

col1, col2, col3 = st.columns(3)

with col1:
    if latest_aaii['Bullish'] > 45:
        st.error(f"🛑 Bullish: {latest_aaii['Bullish']:.1f}% (Extreme optimism)")
    else:
        st.info(f"📈 Bullish: {latest_aaii['Bullish']:.1f}%")

with col2:
    st.info(f"😐 Neutral: {latest_aaii['Neutral']:.1f}%")

with col3:
    if latest_aaii['Bearish'] > 45:
        st.success(f"🚀 Bearish: {latest_aaii['Bearish']:.1f}% (Extreme fear)")
    else:
        st.info(f"📉 Bearish: {latest_aaii['Bearish']:.1f}%")
