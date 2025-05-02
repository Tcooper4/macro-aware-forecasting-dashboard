import streamlit as st

st.set_page_config(page_title="Home", page_icon="📊", layout="wide")

st.title("📊 Macro-Aware Forecasting Dashboard")

st.markdown("""
Welcome to the **Macro-Aware Forecasting Dashboard** — a multi-model, regime-sensitive platform for exploring financial predictions, trade signals, and portfolio strategies.

### 🔍 What You Can Do:
- **Forecast & Trade**: Use AI and statistical models to generate trading signals.
- **Portfolio Optimization**: Allocate assets for maximum Sharpe Ratio — with regime switching logic.
- **Strategy Settings**: Adjust your risk tolerance, trade frequency, or fine-tune expert model parameters.
- **Expert Settings**: Modify ARIMA, GARCH, LSTM, HMM, and ML model behavior.
- **Glossary & Guide**: Learn how each model works — even if you're new to trading.

---

Use the sidebar to navigate through the tools. Each section includes explanations for both beginners and experts.
""")
