import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

from features.strategy_engine import calculate_indicators, generate_signal
from models.arima_model import forecast_arima
from models.garch_model import forecast_garch
from models.hmm_model import detect_regimes
from models.ml_models import prepare_ml_data, predict_xgboost, predict_random_forest, predict_logistic
from models.ensemble import ensemble_vote

# --- Streamlit Page Setup ---
st.set_page_config(page_title="📈 Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Assistant")
st.caption("Advanced multi-model trade signals and forecast analysis")

# --- User Inputs ---
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

# --- Main Logic ---
if st.button("Run Forecast & Signals"):
    df = fetch_data(ticker_input, start=start_date, end=end_date)

    st.subheader("🔎 Raw Debug Info")
    st.write("Data shape:", df.shape)
    st.dataframe(df.head())

    if df.empty or len(df) < 30:
        st.error("❌ Not enough data returned. Try a different ticker or date range.")
        st.stop()

    # --- Rule-Based Strategy ---
    rule_df = calculate_indicators(df.copy())
    rule_signal = generate_signal(rule_df)

    st.metric("📊 Rule-Based Signal", rule_signal["Signal"])
    st.write(f"📉 Volatility: {rule_signal['Volatility']}")
    st.write(f"📐 Suggested Position Size: {rule_signal['Position Size']}")
    st.write(f"🧠 Votes: {rule_signal['Votes']}")
    st.line_chart(rule_df["Close"])

    # --- Machine Learning Models ---
    X, y = prepare_ml_data(rule_df)
    X_train, X_test = X[:-forecast_days], X[-forecast_days:]
    y_train = y[:-forecast_days]

    pred1, conf1 = predict_xgboost(X_train, y_train, X_test)
    pred2, conf2 = predict_random_forest(X_train, y_train, X_test)
    pred3, conf3 = predict_logistic(X_train, y_train, X_test)

    # --- Ensemble Decision ---
    final_signal, final_conf = ensemble_vote(
        [pred1, pred2, pred3], [conf1, conf2, conf3]
    )
    st.metric("🧠 Ensemble ML Signal", final_signal)
    st.write(f"🔎 ML Confidence Score: {final_conf:.2f}")

    # --- ARIMA Forecast ---
    arima_forecast = forecast_arima(rule_df["Close"], steps=forecast_days)
    st.subheader("🔮 ARIMA Forecast")
    st.line_chart(arima_forecast)

    # --- GARCH Forecast ---
    garch_var = forecast_garch(rule_df["Close"], steps=forecast_days)
    st.metric("📉 Forecasted Volatility (GARCH)", f"{garch_var[-1]:.2f}")

    # --- HMM Regimes ---
    states = detect_regimes(rule_df["Close"], n_states=3)
    rule_df["Regime"] = states
    st.subheader("📊 Regime Detection (HMM)")
    st.line_chart(rule_df["Regime"])

    # --- Export Summary ---
    summary = pd.DataFrame([{
        "Ticker": ticker_input,
        "Rule Signal": rule_signal["Signal"],
        "ML Ensemble Signal": final_signal,
        "Confidence Score": final_conf,
        "Volatility": rule_signal["Volatility"],
        "Votes": ", ".join(rule_signal["Votes"])
    }])
    st.subheader("📋 Signal Summary")
    st.dataframe(summary)
    csv = summary.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Signal CSV", csv, "forecast_summary.csv", "text/csv")
