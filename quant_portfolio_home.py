import streamlit as st

st.set_page_config(page_title="Tcooper Quant Portfolio", layout="centered")

st.title("🚀 Tcooper Quant Portfolio Projects")

st.write("""
Welcome to my curated collection of **Quantitative Finance** and **Data Science** dashboards. 
Each project demonstrates advanced modeling, forecasting, optimization, and macroeconomic analysis skills.

🔍 Click a project below to explore live demos:
""")

st.page_link("https://macro-aware-forecasting-dashboard.streamlit.app", label="📈 Macro-Aware Forecasting Dashboard", icon="📈")
st.page_link("https://macro-aware-forecasting-dashboard.streamlit.app/portfolio_dashboard", label="📊 Portfolio Optimization & Efficient Frontier", icon="📊")
st.page_link("https://macro-aware-forecasting-dashboard.streamlit.app/trade_recommendations", label="🛒 Trade Recommendation Engine", icon="🛒")
st.page_link("https://macro-aware-forecasting-dashboard.streamlit.app/macro_sentiment_dashboard", label="🌎 Macro Sentiment Analysis Dashboard", icon="🌎")

st.markdown("""
---

Built with ❤️ using **Streamlit**, **Prophet**, **ARIMA**, **LSTM**, and live market data from **Yahoo Finance**, **FRED**, and **MarketWatch**.

For updates and source code visit: [GitHub Repository](https://github.com/Tcooper4/macro-aware-forecasting-dashboard)
""")
