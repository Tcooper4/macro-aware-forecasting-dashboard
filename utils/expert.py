import streamlit as st

def get_expert_settings():
    return st.session_state.get("expert_settings", {})
