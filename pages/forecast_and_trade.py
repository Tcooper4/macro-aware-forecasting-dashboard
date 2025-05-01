import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
from features.strategy_engine import calculate_indicators, generate_signal

# --- Streamlit Page Setup ---
st.set_page_config(page_title="📈 Forecast & Trade", layout="wide")
st.title("📈 Forecast & Trade Assistant")
st.caption("Advanced multi-indicator trade signals and forecast analysis")

# --- User Inputs ---
tickers_input = st.text_input("Enter ticker(s), comma-separated", value="SPY")
forecast_days = st.slider("Forecast horizon (ARIMA)", 1, 30, 5)
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End date", pd.to_datetime("today"))

tickers_raw = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = tickers_raw  # always a list for consistency

# --- Alpha Vantage Fetch ---
@st.cache_data
def fetch_data(ticker, start=None, end=None):
    api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
    ts = TimeSeries(key=api_key, output_format="pandas")

    try:
        df, _ = ts.get_daily_adjusted(symbol=ticker, outputsize="full")
        df = df.rename(columns={
            "5. adjusted close": "Close",
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "6. volume": "Volume"
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

# --- Main Execution ---
if st.button("Run Forecast & Signals"):
    ticker = tickers[0]
    data = fetch_data(ticker, start=start_date, end=end_date)

    st.subheader("🔎 Raw Debug Info")
    st.write("Ticker:", ticker)
    st.write("Data shape:", data.shape)
    st.dataframe(data.head())

    if data.empty or len(data) == 0:
        st.error("❌ No data returned. Try a different ticker or date range.")
        st.stop()

    try:
        df = data[["Close"]].dropna().copy()
        df = calculate_indicators(df)

        if len(df) < 30:
            st.warning(f"{ticker}: Not enough data for signal generation.")
        else:
            signal_result = generate_signal(df)
            signal = signal_result["Signal"]
            score = signal_result["Score"]
            vol = signal_result["Volatility"]
            pos_size = signal_result["Position Size"]
            votes = signal_result["Votes"]

            # Show output
            st.metric(label=f"🚦 Signal for {ticker}", value=signal)
            st.write(f"🧠 Model Votes: {votes}")
            st.write(f"📊 Confidence Score: {score}")
            st.write(f"📉 Estimated Volatility: {vol}")
            st.write(f"📐 Suggested Position Size: {pos_size}")
            st.line_chart(df["Close"])

            # Export CSV
            result_df = pd.DataFrame([{
                "Ticker": ticker,
                "Signal": signal,
                "Score": score,
                "Volatility": vol,
                "Position Size": pos_size,
                "Votes": ", ".join(votes)
            }])
            st.subheader("📋 Signal Summary")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Signal CSV", csv, "trade_signals.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ Signal generation failed: {e}")
