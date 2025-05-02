import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Trade Recommendations", layout="wide")
st.title("📈 Daily Trade Recommendations (S&P 500 Scan)")

data_path = "data/top_trades.csv"

if not os.path.exists(data_path):
    st.warning("Trade data not yet generated. Please run the scanner.")
    st.stop()

df = pd.read_csv(data_path)

st.markdown("These are the top trade opportunities for today based on model consensus, market regime, and your strategy settings.")

st.dataframe(df, use_container_width=True)

# Optional: Show trade ideas summary
st.markdown("### 🧠 Trade Summary")
for i, row in df.iterrows():
    st.markdown(f"""
    **{row['Ticker']}** → **{row['Signal']}**
    - 📊 Action: `{row['Action']}` — Size: `{row['Size']}%`
    - 🧠 Reason: {row['Rationale']}
    - 📉 Regime: {row['Regime']} | Confidence: `{row['Confidence']:.2%}`
    """)
