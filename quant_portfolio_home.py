import streamlit as st

st.set_page_config(page_title="Tcooper Quant Portfolio", layout="centered")

st.title("🚀 Tcooper Quant Portfolio Projects")

st.write("""
Welcome to my collection of Quantitative Finance and Data Science dashboards.  
Explore live interactive projects below:
""")

st.page_link("https://tcooper.streamlit.app", label="📈 Macro-Aware Forecasting Dashboard")

# Future: you can add more dashboards here when you build them
# Example:
# st.page_link("https://yoursecondproject.streamlit.app", label="📊 Portfolio Optimization Model")
