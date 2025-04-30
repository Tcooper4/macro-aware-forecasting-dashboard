import streamlit as st

st.set_page_config(page_title="Strategy Settings", layout="wide")
st.title("⚙️ Strategy Settings")

st.info("Adjust your trading strategy thresholds and indicator settings. These preferences will affect trade recommendations across all modules.")

# --- RSI Settings ---
st.subheader("📉 RSI Thresholds")
rsi_buy = st.slider("RSI Buy Threshold", 0, 50, st.session_state.get("rsi_buy", 30))
rsi_sell = st.slider("RSI Sell Threshold", 50, 100, st.session_state.get("rsi_sell", 70))
rsi_lookback = st.slider("RSI Lookback Period", 5, 30, st.session_state.get("rsi_lookback", 14))

# --- MACD Settings ---
st.subheader("📈 MACD Settings")
macd_fast = st.slider("Fast EMA Period", 5, 20, st.session_state.get("macd_fast", 12))
macd_slow = st.slider("Slow EMA Period", 10, 30, st.session_state.get("macd_slow", 26))
macd_signal = st.slider("Signal EMA Period", 5, 15, st.session_state.get("macd_signal", 9))

# --- EMA Crossover Settings ---
st.subheader("🪜 EMA Crossover Settings")
ema_fast = st.slider("Fast EMA", 5, 20, st.session_state.get("ema_fast", 8))
ema_slow = st.slider("Slow EMA", 10, 50, st.session_state.get("ema_slow", 21))

# --- Strategy Toggles ---
st.subheader("📊 Strategy Toggles")
enable_rsi = st.checkbox("Enable RSI Strategy", st.session_state.get("enable_rsi", True))
enable_macd = st.checkbox("Enable MACD Cross", st.session_state.get("enable_macd", True))
enable_ema = st.checkbox("Enable EMA Crossover", st.session_state.get("enable_ema", True))

# --- Save Settings ---
if st.button("✅ Save Settings"):
    st.session_state["rsi_buy"] = rsi_buy
    st.session_state["rsi_sell"] = rsi_sell
    st.session_state["rsi_lookback"] = rsi_lookback

    st.session_state["macd_fast"] = macd_fast
    st.session_state["macd_slow"] = macd_slow
    st.session_state["macd_signal"] = macd_signal

    st.session_state["ema_fast"] = ema_fast
    st.session_state["ema_slow"] = ema_slow

    st.session_state["enable_rsi"] = enable_rsi
    st.session_state["enable_macd"] = enable_macd
    st.session_state["enable_ema"] = enable_ema

    st.success("✅ Strategy settings saved across app.")
