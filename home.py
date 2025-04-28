import streamlit as st

st.set_page_config(page_title="Home - Quant Platform", layout="wide")

st.title("🚀 Welcome to Your Quant Forecasting Platform")

st.markdown("### What would you like to do today?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 Macro Dashboard"):
        st.switch_page("dashboard.py")

with col2:
    if st.button("📊 Portfolio Optimizer"):
        st.switch_page("pages/portfolio_optimizer.py")

with col3:
    if st.button("🛒 Daily Trade Recommendations"):
        st.switch_page("pages/trade_recommendations.py")
