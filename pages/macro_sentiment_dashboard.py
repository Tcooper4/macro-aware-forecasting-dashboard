import streamlit as st
import yfinance as yf
import pandas as pd

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

# Coming next: AAII Sentiment, Put/Call Ratio
st.markdown("---")
st.caption("More sentiment indicators coming soon: AAII Survey, Put/Call Ratio 🚀")
