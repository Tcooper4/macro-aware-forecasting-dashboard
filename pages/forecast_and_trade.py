import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
import datetime

# --- Import model layers ---
from features.strategy_engine import calculate_indicators, generate_signal
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import detect_regimes
from models.ml_models import prepare_ml_data, predict_xgboost, predict_random_forest, predict_logistic
from models.ensemble import ensemble_vote
from models.lstm_model import train_lstm

# --- Page setup ---
st.set_page_config(page_title="📈 Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Assistant")
st.caption("Multi-model trade signals and interactive forecasting")

# --- Inputs ---
ticker_input = st.text_input("Enter Ticker", value="SPY")
forecast_days = st.slider("Forecast Horizon (Days)", 1, 30, 5)
start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

# --- Alpha Vantage Fetch ---
@st.cache_data
def fetch_data(ticker, start=None, end=None):
    api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
    ts = TimeSeries(key=api_key, output_format="pandas")
    try:
        df, _ = ts.get_daily(symbol=ticker, outputsize="full")
        df = df.rename(columns={
            "4. close": "Close",
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "5. volume": "Volume"
        })
        df = df[["Close", "High", "Low", "Open", "Volume"]]
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        if start:
            df = df[df.index >= pd.to_datetime(start)]
        if end:
            df = df[df.index <= pd.to_datetime(end)]
        return df
    except Exception as e:
        st.error(f"❌ Alpha Vantage fetch error: {e}")
        return pd.DataFrame()

# --- Run Analysis ---
if st.button("Run Forecast & Signals"):
    df = fetch_data(ticker_input, start=start_date, end=end_date)
    st.subheader("🔎 Raw Data")
    st.write(df.tail())
    
    if df.empty or len(df) < 60:
        st.error("❌ Not enough data. Try a longer date range.")
        st.stop()

    # Rule-based strategy
    strategy_df = calculate_indicators(df.copy())
    rule_result = generate_signal(strategy_df)

    st.metric("📊 Rule-Based Signal", rule_result["Signal"])
    st.write("📉 Volatility:", rule_result["Volatility"])
    st.write("📐 Suggested Position Size:", rule_result["Position Size"])
    st.write("🧠 Votes:", rule_result["Votes"])
    st.line_chart(strategy_df["Close"])

    # ML-based forecast
    X, y = prepare_ml_data(strategy_df)
    X_train, X_test = X[:-forecast_days], X[-forecast_days:]
    y_train = y[:-forecast_days]

    pred1, conf1 = predict_xgboost(X_train, y_train, X_test)
    pred2, conf2 = predict_random_forest(X_train, y_train, X_test)
    pred3, conf3 = predict_logistic(X_train, y_train, X_test)

    final_signal, final_conf = ensemble_vote([pred1, pred2, pred3], [conf1, conf2, conf3])
    st.metric("🧠 Ensemble ML Signal", final_signal)
    st.write("🔍 Confidence:", round(final_conf, 2))

    # --- ARIMA Forecast ---
    try:
        arima_forecast = forecast_arima(df["Close"], steps=forecast_days)
        future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days)
        st.subheader("🔮 ARIMA Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Historical"))
        fig.add_trace(go.Scatter(x=future_dates, y=arima_forecast, mode="lines+markers", name="ARIMA Forecast"))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ ARIMA failed: {e}")

    # --- GARCH Volatility ---
    try:
        garch = forecast_garch(df["Close"], steps=forecast_days)
        st.metric("📉 GARCH Volatility Forecast", f"{garch[-1]:.2f}")
    except Exception as e:
        st.error(f"❌ GARCH failed: {e}")

    # --- HMM Regimes ---
    try:
        regimes = detect_regimes(df["Close"], n_states=3)
        df["Regime"] = regimes
        st.subheader("📊 HMM Regimes")
        st.line_chart(df["Regime"])
    except Exception as e:
        st.error(f"❌ HMM failed: {e}")

    # --- LSTM Forecast ---
    try:
        lstm = train_lstm(df["Close"], look_back=60, forecast_horizon=forecast_days)
        future_lstm = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days)
        st.subheader("🧠 LSTM Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Historical"))
        fig.add_trace(go.Scatter(x=future_lstm, y=lstm, mode="lines+markers", name="LSTM Forecast"))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ LSTM failed: {e}")

    # --- Signal Summary ---
    summary = pd.DataFrame([{
        "Ticker": ticker_input,
        "Rule Signal": rule_result["Signal"],
        "ML Ensemble Signal": final_signal,
        "ML Confidence": round(final_conf, 2),
        "Volatility": rule_result["Volatility"],
        "Votes": ", ".join(rule_result["Votes"])
    }])
    st.subheader("📋 Final Signal Summary")
    st.dataframe(summary)
    csv = summary.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Forecast Summary", csv, "forecast_summary.csv", "text/csv")
