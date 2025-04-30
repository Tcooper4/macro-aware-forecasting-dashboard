import streamlit as st
import pandas as pd
import yfinance as yf
from features.tech_indicators import calculate_indicators
from features.strategies import generate_trade_signals
import datetime

st.set_page_config(page_title="Trade Recommendations", layout="wide")
st.title("📈 Daily Trade Recommendations")

# --- Settings ---
st.sidebar.header("⚙️ Settings")
tickers = st.sidebar.text_input("Enter Tickers (comma-separated)", "AAPL, MSFT, TSLA, NVDA, AMZN")
tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

start_date = st.sidebar.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=90))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
lookback_period = st.sidebar.slider("Lookback Period (days)", 5, 60, 14)
signal_type = st.sidebar.selectbox("Strategy", ["RSI Strategy", "MACD Cross", "EMA Crossover"])

if st.sidebar.button("🔍 Run Screening"):
    results = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if df.empty:
                continue

            df = calculate_indicators(df, lookback=lookback_period)
            signal = generate_trade_signals(df, strategy=signal_type)
            last_signal = signal.iloc[-1]

            results.append({
                "Ticker": ticker,
                "Close": df["Close"].iloc[-1],
                "RSI": df["RSI"].iloc[-1],
                "MACD Signal": df["MACD_Signal"].iloc[-1],
                "MACD": df["MACD"].iloc[-1],
                "EMA Fast": df["EMA_Fast"].iloc[-1],
                "EMA Slow": df["EMA_Slow"].iloc[-1],
                "Signal": last_signal
            })
        except Exception as e:
            st.warning(f"⚠️ {ticker} failed: {e}")

    if results:
        df_signals = pd.DataFrame(results)
        st.subheader("📋 Today's Recommendations")
        st.dataframe(df_signals.style.format({"Close": "${:.2f}", "RSI": "{:.1f}"}))

        csv = df_signals.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Signal CSV", csv, file_name="trade_signals.csv")
    else:
        st.warning("No valid data returned. Please check ticker list or date range.")
