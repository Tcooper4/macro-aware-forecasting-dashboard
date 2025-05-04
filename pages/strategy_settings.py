st.set_page_config(page_title="Strategy Settings", layout="wide")

import streamlit as st

st.title("⚙️ Strategy Settings")

st.info("Use this page to configure both your high-level trading strategy and low-level model behavior. Ideal for both beginners and expert users.")

# --- Templates ---
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

template = st.selectbox("🎯 Choose a Strategy Template", list(templates.keys()))
default = templates[template]

# --- Core Settings ---
st.markdown("### 🔧 Core Strategy Settings")

st.markdown("**🧱 Risk Tolerance**\n- Low: Small positions, low volatility\n- Medium: Balanced\n- High: Larger trades, more volatility")
risk = st.selectbox("Risk Level", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(default["risk_tolerance"]))

st.markdown("**🔁 Trade Frequency**\n- Daily: Reacts quickly to signals\n- Weekly: Less frequent trades")
frequency = st.selectbox("Trade Frequency", ["Daily", "Weekly"], index=["Daily", "Weekly"].index(default["trade_frequency"]))

st.markdown("**📏 Sizing Method**\n- Fixed: Static trade size\n- Dynamic: Varies based on model output or confidence")
sizing = st.selectbox("Position Sizing", ["Fixed", "Dynamic"], index=["Fixed", "Dynamic"].index(default["position_sizing"]))

# --- Save Core Strategy Settings ---
st.session_state["strategy_settings"] = {
    "risk_tolerance": risk,
    "trade_frequency": frequency,
    "position_sizing": sizing
}

# --- Expert Toggle ---
st.markdown("---")
expert_mode = st.toggle("🔧 Enable Expert Settings")

if expert_mode:
    st.markdown("### 🧠 Expert Model Settings")

    # ARIMA
    st.subheader("📈 ARIMA")
    arima_p = st.number_input("ARIMA p (lags)", 0, 10, 5)
    arima_d = st.number_input("ARIMA d (difference)", 0, 2, 1)
    arima_q = st.number_input("ARIMA q (MA)", 0, 10, 0)

    # GARCH
    st.subheader("📉 GARCH")
    garch_p = st.number_input("GARCH p", 1, 3, 1)
    garch_q = st.number_input("GARCH q", 1, 3, 1)

    # HMM
    st.subheader("🔀 HMM")
    hmm_states = st.slider("Hidden States", 1, 5, 2)

    # LSTM
    st.subheader("🧠 LSTM")
    lstm_units = st.number_input("Hidden Units", 10, 200, 50)
    lstm_epochs = st.number_input("Epochs", 1, 100, 5)

    # ML
    st.subheader("📊 ML Model")
    ml_type = st.selectbox("Model Type", ["Random Forest", "XGBoost"])
    ml_estimators = st.number_input("Estimators", 10, 1000, 100)
    ml_depth = st.number_input("Max Depth", 1, 10, 3)

    st.session_state["expert_settings"] = {
        "arima_order": (arima_p, arima_d, arima_q),
        "garch_order": (garch_p, garch_q),
        "hmm_states": hmm_states,
        "lstm": {"units": lstm_units, "epochs": lstm_epochs},
        "ml": {"type": ml_type, "n_estimators": ml_estimators, "max_depth": ml_depth}
    }

    st.success("Expert settings saved.")

# --- Final Summary ---
st.markdown("---")
st.markdown("### 🧾 Summary")
st.write(f"**Template:** {template}")
st.write(f"**Risk:** {risk} | **Frequency:** {frequency} | **Sizing:** {sizing}")
if expert_mode:
    st.json(st.session_state["expert_settings"])

# --- Accessors ---
def get_user_strategy_settings():
    return st.session_state.get("strategy_settings", {
        "risk_tolerance": "Medium",
        "trade_frequency": "Weekly",
        "position_sizing": "Fixed"
    })

def get_expert_settings():
    return st.session_state.get("expert_settings", {})
