import streamlit as st

st.set_page_config(page_title="Glossary", layout="wide")
st.title("📘 Glossary & Education")

st.markdown("""
### ❓ What is a Forecast Model?
A model is a mathematical formula that tries to predict the future based on past patterns in the data.

### 📊 Types of Models:
- **ARIMA**: Time series model based on trends and seasonality
- **GARCH**: Focuses on volatility and risk
- **HMM**: Detects hidden market regimes (bull vs bear)
- **LSTM**: Deep learning model that remembers past patterns
- **XGBoost/Random Forest**: Machine learning models trained on returns

### 📌 Trade Signals:
- **BUY**: Expected increase in price
- **SELL**: Expected drop
- **HOLD**: Unclear direction

### 📈 Forecast Horizon:
How far ahead the models are trying to predict (1 Day, 1 Week, 1 Month)

---

Still lost? Toggle "Beginner Mode" on the homepage for simpler explanations.
""")
