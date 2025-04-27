import streamlit as st

def navigation_bar():
    st.markdown("---")
    cols = st.columns(4)

    with cols[0]:
        if st.button("🏠 Home"):
            st.switch_page("home.py")
    with cols[1]:
        if st.button("📈 Macro Dashboard"):
            st.switch_page("macro_dashboard.py")
    with cols[2]:
        if st.button("📊 Portfolio Optimizer"):
            st
