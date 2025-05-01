import streamlit as st

def get_user_strategy_settings():
    st.sidebar.header("⚙️ Strategy Settings")
    risk = st.sidebar.selectbox("Risk Tolerance", ["Low", "Medium", "High"], index=1)
    freq = st.sidebar.selectbox("Trade Frequency", ["Daily", "Weekly"], index=1)
    size = st.sidebar.selectbox("Position Sizing", ["Fixed", "Dynamic"], index=1)
    return {
        "risk_tolerance": risk,
        "trade_frequency": freq,
        "position_sizing": size
    }
