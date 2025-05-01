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
st.caption("Multi-asset ARIMA, GARCH, and HMM-based market analysis")

# --- User Inputs ---
tickers_input = st.text_input("Enter ticker(s) separated by commas", value="SPY")
forecast_days = st.slider("Forecast horizon (days)", 1, 30, 5)
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End date", pd.to_datetime("today"))

# Clean ticker list
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# --- Fetch Price Data ---
@st.cache_data
def fetch_data(tickers, start, end):
    return yf.download(tickers, start=start, end=end, auto_adjust=True)

if st.button("Run Forecast"):
    data = fetch_data(tickers, start_date, end_date)

    if data.empty:
        st.error("❌ Failed to retrieve any data. Check ticker symbols or date range.")
        st.stop()

    # Detect if multiple tickers returned a multi-index column
    multi_ticker = isinstance(data.columns, pd.MultiIndex)

    st.subheader("📊 Raw Downloaded Data")
    st.dataframe(data.tail())
    st.write("🧾 Columns:", data.columns.tolist())
    st.write("📐 Shape:", data.shape)
    st.dataframe(data.isna().sum())

    for ticker in tickers:
        st.markdown(f"---\n## 📈 {ticker} Forecasting")

        try:
            series = (
                data["Close", ticker] if multi_ticker else data["Close"]
            ).dropna()

            st.write(f"✅ {ticker} series length:", len(series))
            st.line_chart(series)

            if len(series) < 30:
                st.warning(f"{ticker}: Not enough data points for ARIMA. Skipping.")
                continue

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
            st.subheader(f"🔮 ARIMA Forecast for {ticker}")
            st.line_chart(arima_forecast)

            st.subheader(f"📉 GARCH Estimated Volatility for {ticker}")
            st.line_chart(volatility)

            st.subheader(f"📊 HMM Market Regimes for {ticker}")
            fig, ax = plt.subplots()
            ax.plot(series.index[1:], series.values[1:], label="Price")
            ax.scatter(series.index[1:], series.values[1:], c=regimes, cmap="tab10", label="Regime")
            ax.set_title(f"{ticker} Market Regimes")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Error processing {ticker}: {e}")
