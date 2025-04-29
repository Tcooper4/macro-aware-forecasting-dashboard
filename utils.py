import streamlit as st
from pathlib import Path

# Helper function to get the current page
def get_current_page():
    return Path(st.session_state.get("_page_", "")).name.lower()

def navigation_bar():
    st.markdown("""
        <style>
            .nav-button {
                background-color: #f0f2f6;
                border: none;
                padding: 0.6em 1em;
                font-size: 1.1em;
                cursor: pointer;
                border-radius: 8px;
                transition: background-color 0.3s ease;
                width: 100%;
            }
            .nav-button:hover {
                background-color: #d6e4f0;
            }
            .active-button {
                background-color: #add8e6;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")
    cols = st.columns(5)

    pages = [
        ("🏠 Home", "home.py"),
        ("📈 Macro Dashboard", "macro_dashboard.py"),
        ("📊 Portfolio Optimizer", "portfolio_optimizer.py"),
        ("📑 Trade Recommendations", "trade_recommendations.py"),
        ("🌎 Macro Sentiment Dashboard", "pages/macro_sentiment_dashboard.py")
    ]

    current_page = get_current_page()

    for idx, (label, page) in enumerate(pages):
        with cols[idx]:
            btn_style = "active-button" if page.lower() == current_page else "nav-button"
            if st.button(label, key=page):
                st.switch_page(page)

    st.markdown("---")
