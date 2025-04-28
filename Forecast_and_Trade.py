import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from arch import arch_model
from statsmodels.tsa.arima.model import ARIMA
from hmmlearn.hmm import GaussianHMM
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Forecast and Trade", layout="wide", page_icon="📈")

st.title("📈 Forecasts and Trade Recommendations")

# --- Sidebar: User Inputs ---
st.sidebar.header("Customize Forecast")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value='SPY')
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))
forecast_days = st.sidebar.slider("Forecast Horizon (Days)", min_value=5, max_value=60, value=20)

# --- Load Data ---
@st.cache_data
def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Returns'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
    return data.dropna()

data = load_data(ticker, start_date, end_date)

# --- ARIMA Forecast ---
def forecast_arima(series, steps=20):
    model = ARIMA(series, order=(5, 1, 0))
    fitted_model = model.fit()
    forecast = fitted_model.forecast(steps=steps)
    return forecast

# --- GARCH Forecast (Volatility) ---
def forecast_garch(series, steps=20):
    model = arch_model(series * 100, vol='Garch', p=1, q=1)
    fitted_model = model.fit(disp="off")
    forecast = fitted_model.forecast(horizon=steps)
    return np.sqrt(forecast.variance.values[-1])

# --- Regime-Switching (HMM) ---
def forecast_hmm(series):
    model = GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
    model.fit(series.values.reshape(-1, 1))
    hidden_states = model.predict(series.values.reshape(-1, 1))
    return hidden_states

# --- Run Forecasts ---
arima_forecast = forecast_arima(data['Adj Close'], steps=forecast_days)
garch_forecast_vol = forecast_garch(data['Returns'], steps=forecast_days)
hmm_states = forecast_hmm(data['Returns'])

# --- Show Plots ---
st.subheader("📊 Historical Price and Forecast")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], name='Historical'))
future_dates = pd.date_range(data.index[-1], periods=forecast_days + 1, freq='B')[1:]
fig.add_trace(go.Scatter(x=future_dates, y=arima_forecast, name='ARIMA Forecast'))
st.plotly_chart(fig, use_container_width=True)

# --- Trading Recommendation ---
st.subheader("💡 Trade Recommendation")

recent_volatility = np.mean(garch_forecast_vol)
recent_state = hmm_states[-1]

if recent_state == 0 and recent_volatility < 2.0:
    recommendation = "✅ Likely Stable Regime — Consider **Buying** or **Holding**."
elif recent_state == 1 and recent_volatility > 2.5:
    recommendation = "⚠️ High Volatility Regime — Consider **Selling** or **Avoiding**."
else:
    recommendation = "🔎 Neutral/Uncertain Regime — Consider **Waiting**."

st.success(recommendation)
