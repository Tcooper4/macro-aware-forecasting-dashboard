import streamlit as st
import pandas as pd
import os
import openai
import datetime
from io import StringIO

st.set_page_config(page_title="Trade Recommendations", layout="wide")
st.title("📈 Daily Trade Recommendations (S&P 500 Scan)")

# --- Load Data ---
data_path = "data/top_trades.csv"

if not os.path.exists(data_path):
    st.warning("Trade data not yet generated. Please run the scanner.")
    st.stop()

df = pd.read_csv(data_path)

# --- Dynamic fallback if confidence column is missing ---
if "Confidence" not in df.columns:
    df["Confidence"] = 1.0

df = df.sort_values("Confidence", ascending=False)

# --- Controls ---
st.sidebar.header("🔍 Filters")
signals = st.sidebar.multiselect("Filter by Signal", ["BUY", "SELL"], default=["BUY", "SELL"])
regimes = st.sidebar.multiselect("Filter by Regime", df["Regime"].unique(), default=list(df["Regime"].unique()))

df = df[df["Signal"].isin(signals) & df["Regime"].isin(regimes)]

# --- Display Table with Styling ---
st.markdown("These are the top trade opportunities based on model consensus, regime logic, and your strategy settings.")

def highlight_signal(val):
    if val == "BUY":
        return "color: green; font-weight: bold"
    elif val == "SELL":
        return "color: red; font-weight: bold"
    return ""

st.dataframe(df.style.applymap(highlight_signal, subset=["Signal"]), use_container_width=True)

# --- GPT Summary (Optional) ---
if "OPENAI_API_KEY" in os.environ or st.secrets.get("OPENAI_API_KEY"):
    openai.api_key = os.environ.get("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

    st.subheader("🧐 AI Commentary")
    for _, row in df.iterrows():
        prompt = f"""
        You are an expert financial assistant. Interpret the following signal:
        - Ticker: {row['Ticker']}
        - Signal: {row['Signal']}
        - Strategy Action: {row['Action']} ({row['Size']}%)
        - Market Regime: {row['Regime']}
        - Confidence Score: {row['Confidence']:.2%}
        - Rationale: {row['Rationale']}

        Summarize this for a trader in 2 short bullet points.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            bullets = response["choices"][0]["message"]["content"]
            st.markdown(f"**{row['Ticker']} ({row['Signal']})**\n\n{bullets}")
        except Exception as e:
            st.warning(f"OpenAI error for {row['Ticker']}: {e}")
else:
    st.info("Set OPENAI_API_KEY as a secret or environment variable to enable AI commentary.")

# --- Placeholder: Options Analysis ---
st.subheader("📊 Options Analysis (Coming Soon)")
st.markdown("We’ll soon identify ideal calls/puts based on trend, volatility, and momentum.")

# --- Simulated Backtesting for Past Picks ---
st.subheader("📉 Simulated Backtest (Preview)")
days_held = st.slider("Holding period (days)", 1, 30, 5)

def simulate_trade_return(signal, confidence):
    if signal == "BUY":
        return 0.02 * confidence * days_held / 5
    elif signal == "SELL":
        return -0.015 * confidence * days_held / 5
    return 0.0

df["Simulated Return"] = df.apply(lambda row: simulate_trade_return(row["Signal"], row["Confidence"]), axis=1)
total = df["Simulated Return"].sum()
st.metric("📈 Simulated Portfolio Return", f"{total:.2%}")
st.bar_chart(df.set_index("Ticker")["Simulated Return"])
