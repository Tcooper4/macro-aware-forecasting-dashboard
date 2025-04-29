import streamlit as st

st.set_page_config(page_title="🏠 Home - Macro-Aware Quant Platform", layout="wide")

st.title("🏠 Welcome to the Macro-Aware Quant Platform")

st.markdown("""
Explore powerful dashboards combining market data, macroeconomic insights, and machine learning forecasts.
Select a section below to get started:
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📈 Macro Dashboard"):
        st.switch_page("pages/macro_dashboard.py")

with col2:
    if st.button("📊 Portfolio Optimizer"):
        st.switch_page("pages/portfolio_dashboard.py")

with col3:
    if st.button("🛒 Trade Recommendations"):
        st.switch_page("pages/trade_recommendations.py")

with col4:
    if st.button("🌎 Macro Sentiment Dashboard"):
        st.switch_page("pages/macro_sentiment_dashboard.py")

st.markdown("""
---
Built with **Streamlit**, **Prophet**, **ARIMA**, **LSTM**, and live market feeds from **Yahoo Finance**, **FRED**, and **MarketWatch**.
[GitHub Repository](https://github.com/Tcooper4/macro-aware-forecasting-dashboard)
""")
