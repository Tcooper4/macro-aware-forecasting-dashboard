import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from features.strategy_engine import calculate_indicators, generate_signal

st.set_page_config(page_title="📈 Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Assistant")
st.caption("Advanced multi-indicator trade signals and forecast analysis")

# --- Inputs ---
tickers_input = st.text_input("Enter ticker(s), comma-separated", value="SPY")
forecast_days = st.slider("Forecast horizon (ARIMA)", 1, 30, 5)
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End date", pd.to_datetime("today"))

# --- Clean tickers ---
tickers_raw = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = tickers_raw  # always a list

# --- Robust Fetching ---
@st.cache_data
def fetch_data(tickers, start, end):
    try:
        df = yf.download(tickers, start=start, end=end, auto_adjust=True)
        return df
    except Exception as e:
        st.error(f"❌ Data fetch failed: {e}")
        return pd.DataFrame()

if st.button("Run Forecast & Signals"):
    data = fetch_data(tickers, start_date, end_date)

    st.subheader("🔎 Raw Debug Info")
    st.write("Requested tickers:", tickers)
    st.write("Type of data:", type(data))
    st.write("Data shape:", data.shape if hasattr(data, "shape") else "No shape")
    st.dataframe(data.head())

    if data is None or data.empty or len(data) == 0:
        st.error("❌ No data returned. Check ticker spelling or try a broader date range.")
        st.stop()

    multi_ticker = isinstance(data.columns, pd.MultiIndex)
    tickers_to_process = tickers_raw

    results = []

    for ticker in tickers_to_process:
        st.markdown(f"---\n## 📊 {ticker}")

        try:
            series = (
                data["Close", ticker] if multi_ticker else data["Close"]
            ).dropna()

            df = series.to_frame(name="Close")
            df = calculate_indicators(df)

            if len(df) < 30:
                st.warning(f"{ticker}: Not enough data for signal generation.")
                continue

            signal_result = generate_signal(df)
            signal = signal_result["Signal"]
            score = signal_result["Score"]
            vol = signal_result["Volatility"]
            pos_size = signal_result["Position Size"]
            votes = signal_result["Votes"]

            # Display signal info
            st.metric(label=f"🚦 Signal for {ticker}", value=signal)
            st.write(f"🧠 Model Votes: {votes}")
            st.write(f"📊 Confidence Score: {score}")
            st.write(f"📉 Estimated Volatility: {vol}")
            st.write(f"📐 Suggested Position Size: {pos_size}")
            st.line_chart(df["Close"])

            results.append({
                "Ticker": ticker,
                "Signal": signal,
                "Score": score,
                "Volatility": vol,
                "Position Size": pos_size,
                "Votes": ", ".join(votes)
            })

        except Exception as e:
            st.error(f"❌ Error processing {ticker}: {e}")

    # --- CSV export ---
    if results:
        df_signals = pd.DataFrame(results)
        st.subheader("📋 Signal Summary")
        st.dataframe(df_signals)

        csv = df_signals.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Signal CSV", csv, "trade_signals.csv", "text/csv")
