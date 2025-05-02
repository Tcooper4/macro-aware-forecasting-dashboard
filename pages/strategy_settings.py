import streamlit as st

st.set_page_config(page_title="Strategy Settings", layout="wide")
st.title("⚙️ Strategy Settings")

st.info("Configure your personal trading strategy settings. These options control how the system sizes positions, how frequently trades are made, and how much risk you take.")

# --- Template Profiles ---
templates = {
    "Conservative": {
        "risk_tolerance": "Low",
        "trade_frequency": "Weekly",
        "position_sizing": "Fixed"
    },
    "Balanced": {
        "risk_tolerance": "Medium",
        "trade_frequency": "Weekly",
        "position_sizing": "Fixed"
    },
    "Aggressive": {
        "risk_tolerance": "High",
        "trade_frequency": "Daily",
        "position_sizing": "Dynamic"
    }
}

selected_template = st.selectbox("🎯 Choose a Strategy Template", list(templates.keys()))

# Apply template defaults
default = templates[selected_template]

st.markdown("---")
st.markdown("### 🔍 Setting Explanations")

# --- Risk Tolerance ---
st.markdown("#### 🧱 Risk Tolerance")
st.markdown("""
- **Low**: Smaller position sizes, less exposure to volatility.
- **Medium**: Balanced risk, suitable for most users.
- **High**: Larger trades, more exposure to gains *and* losses.
""")
risk = st.selectbox("Risk Level", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(default["risk_tolerance"]))

# --- Trade Frequency ---
st.markdown("#### 🔁 Trade Frequency")
st.markdown("""
- **Daily**: Reacts quickly to new signals, more trades.
- **Weekly**: Slower updates, lower transaction costs.
""")
frequency = st.selectbox("How often should trades be placed?", ["Daily", "Weekly"], index=["Daily", "Weekly"].index(default["trade_frequency"]))

# --- Sizing Method ---
st.markdown("#### 📏 Position Sizing Method")
st.markdown("""
- **Fixed**: Always trades a fixed portion (e.g. 100% or 50%).
- **Dynamic**: Adjusts trade size based on risk profile or confidence.
""")
sizing = st.selectbox("How should trade size be determined?", ["Fixed", "Dynamic"], index=["Fixed", "Dynamic"].index(default["position_sizing"]))

# --- Save to session state ---
st.session_state["strategy_settings"] = {
    "risk_tolerance": risk,
    "trade_frequency": frequency,
    "position_sizing": sizing
}

st.markdown("---")
st.markdown("### ✅ Final Settings Summary")
st.write(f"- **Template:** {selected_template}")
st.write(f"- **Risk:** `{risk}`")
st.write(f"- **Frequency:** `{frequency}`")
st.write(f"- **Sizing:** `{sizing}`")

# --- Access function for internal use ---
def get_user_strategy_settings():
    return st.session_state.get("strategy_settings", {
        "risk_tolerance": "Medium",
        "trade_frequency": "Weekly",
        "position_sizing": "Fixed"
    })
