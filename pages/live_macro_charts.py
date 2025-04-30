import streamlit as st

st.set_page_config(page_title="Macroeconomic Charts", layout="wide")

st.title("🌐 Live Macroeconomic Charts")
st.caption("This section will include real-time visualizations of key macroeconomic indicators.")

st.markdown("---")

st.info("""
🚧 **Live macroeconomic charts are currently under development.**  
Soon, you’ll be able to explore interactive, real-time data on interest rates, inflation, unemployment, GDP, and more.

📊 Planned features include:
- Interactive line charts for FRED indicators
- Multi-country economic comparisons
- Dynamic annotations (e.g. rate hikes, recessions)
- Theme toggle for light/dark charts
""")

st.markdown("---")

st.button("🔄 Refresh (Coming Soon)", disabled=True)
