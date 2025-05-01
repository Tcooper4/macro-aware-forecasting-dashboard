import streamlit as st
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from hmmlearn.hmm import GaussianHMM
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="📈 Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Assistant")
st.caption("ARIMA, GARCH, and HMM-based market analysis")

# --- User Inputs ---
ticker = st.text_input("Enter stock ticker", value="SPY")
forecast_days = st.slider("Forecast horizon (days)", 1, 30, 5)
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End date", pd.to_datetime("today"))

# --- Fetch Price Data ---
@st.cache_data
def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)
    return data

if st.button("Run Forecast"):
    data = fetch_data(ticker, start_date, end_date)
    
    st.subheader("📊 Price Data Preview")
    st.dataframe(data.tail())

    if "Adj Close" not in data.columns:
        st.error("⚠️ 'Adj Close' column not found in data.")
        st.stop()

    series = data["Adj Close"].dropna()
    st.write("✅ Series length:", len(series))
    st.line_chart(series)

    if len(series) < 30:
        st.warning("Time series too short for ARIMA. Try a different date range.")
        st.stop()

    # --- ARIMA Forecast ---
    def forecast_arima(series, steps=5):
        model = ARIMA(series, order=(1, 1, 1))
        fitted_model = model.fit()
        forecast = fitted_model.forecast(steps=steps)
        return forecast

    arima_forecast = forecast_arima(series, steps=forecast_days)

    # --- GARCH Volatility ---
    def estimate_volatility(series):
        returns = 100 * series.pct_change().dropna()
        model = arch_model(returns, vol="Garch", p=1, q=1)
        garch_fit = model.fit(disp="off")
        return garch_fit.conditional_volatility

    volatility = estimate_volatility(series)

    # --- HMM Regime Detection ---
    def detect_regime(series, n_states=3):
        log_returns = np.log(series / series.shift(1)).dropna().values.reshape(-1, 1)
        model = GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)
        model.fit(log_returns)
        hidden_states = model.predict(log_returns)
        return hidden_states

    regimes = detect_regime(series)

    # --- Display Results ---
    st.subheader("🔮 ARIMA Forecast")
    st.line_chart(arima_forecast)

    st.subheader("📉 GARCH Estimated Volatility")
    st.line_chart(volatility)

    st.subheader("📊 Detected Market Regimes (HMM)")
    fig, ax = plt.subplots()
    ax.plot(series.index[1:], series.values[1:], label="Price")
    ax.scatter(series.index[1:], series.values[1:], c=regimes, cmap="tab10", label="Regime")
    ax.set_title("Market Regimes")
    st.pyplot(fig)
