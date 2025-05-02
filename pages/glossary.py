import streamlit as st

st.set_page_config(page_title="Glossary", layout="wide")
st.title("📘 Trading Glossary")

st.markdown("""
### ❓ What is a Forecast Model?
Forecast models attempt to predict future prices based on past patterns.

### 📊 Models Used:
- **ARIMA**: Forecasts trends based on past prices
- **GARCH**: Estimates market volatility
- **HMM**: Detects hidden market states
- **LSTM**: Neural network that remembers time sequences
- **XGBoost**: Machine learning model using technical features

### 💡 Signal Types:
- **BUY**: Price is expected to rise
- **SELL**: Price is expected to fall
- **HOLD**: No strong directional signal

### 🛠️ Strategy Inputs:
- **Risk Tolerance**: Controls position size
- **Frequency**: How often trades are made
- **Sizing**: Whether trades use fixed or dynamic percentages
""")
