import streamlit as st
import pandas_datareader.data as web
import plotly.graph_objects as go
import datetime
import wbdata
import pandas as pd

# --- Config ---
st.set_page_config(page_title="Live Macroeconomic Charts", layout="wide")
st.title("🌐 Live Macroeconomic Charts")

# --- Date Range ---
start_year = st.sidebar.slider("Start Year", 1960, 2023, 2000)
end_year = st.sidebar.slider("End Year", 1960, 2023, 2023)
start_date = datetime.datetime(start_year, 1, 1)
end_date = datetime.datetime(end_year, 12, 31)
refresh = st.sidebar.button("🔄 Refresh")

# --- FRED Series ---
fred_series = st.sidebar.selectbox("📈 FRED Indicator", [
    "FEDFUNDS",    # Federal Funds Rate
    "CPIAUCSL",    # CPI
    "UNRATE",      # Unemployment
    "GDPC1"        # Real GDP
])
fred_label_map = {
    "FEDFUNDS": "Federal Funds Rate",
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
    "GDPC1": "Real GDP"
}

# --- World Bank Indicators ---
indicator_map = {
    "GDP (current US$)": "NY.GDP.MKTP.CD",
    "Inflation (CPI %)": "FP.CPI.TOTL.ZG",
    "Unemployment Rate (%)": "SL.UEM.TOTL.ZS"
}
co2_indicators = {
    "CO₂ - Bunker Fuels": "CC.CO2.EMSE.BF",
    "CO₂ - Buildings": "CC.CO2.EMSE.BL",
    "CO₂ - Electricity & Heat": "CC.CO2.EMSE.EH",
    "CO₂ - Total Energy": "CC.CO2.EMSE.EN",
    "CO₂ - Industrial Processes": "CC.CO2.EMSE.IP",
    "CO₂ - Transportation": "CC.CO2.EMSE.TR",
    "CO₂ - Coal (Operating)": "CC.COAL.EMIS.CO",
    "CO₂ - Coal (Proposed)": "CC.COAL.EMPR.CO"
}

# --- Country List ---
all_countries = wbdata.get_countries()
country_dict = {c["name"]: c["id"] for c in all_countries if c["region"]["id"] != "NA"}
selected_countries = st.sidebar.multiselect("🌍 Select Countries", options=sorted(country_dict.keys()), default=["United States", "Germany"])

# --- Tabs ---
tabs = st.tabs(["📊 FRED", "🌍 GDP", "📈 Inflation", "📉 Unemployment", "🌫 CO₂ Emissions"])

# --- FRED Tab ---
with tabs[0]:
    try:
        st.subheader(f"{fred_label_map[fred_series]} Over Time")
        fred_data = web.DataReader(fred_series, "fred", start_date, end_date)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fred_data.index, y=fred_data[fred_series], mode='lines'))

        fig.add_vrect(x0="2008-09-01", x1="2009-06-30", fillcolor="red", opacity=0.2,
                      annotation_text="2008 Recession", annotation_position="top left")
        fig.update_layout(title=fred_label_map[fred_series], xaxis_title="Date", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

        st.download_button("📥 Download FRED CSV", fred_data.to_csv().encode('utf-8'), file_name=f"{fred_series}_fred.csv")
    except Exception as e:
        st.error(f"Failed to load FRED data: {e}")

# --- Helper for World Bank Tabs ---
def render_world_bank_chart(label, indicator_code):
    try:
        st.subheader(f"{label} ({start_year}–{end_year})")
        selected_iso = [country_dict[c] for c in selected_countries]
        raw_df = wbdata.get_dataframe({indicator_code: label}, country=selected_iso).reset_index()

        if 'country' not in raw_df.columns and len(selected_countries) == 1:
            raw_df['country'] = selected_countries[0]

        raw_df['date'] = pd.to_datetime(raw_df['date'], format='%Y')
        filtered_df = raw_df[(raw_df['date'] >= start_date) & (raw_df['date'] <= end_date)]
        pivot_df = filtered_df.pivot(index='date', columns='country', values=label)

        fig = go.Figure()
        for country in pivot_df.columns:
            fig.add_trace(go.Scatter(x=pivot_df.index, y=pivot_df[country], mode='lines', name=country))

        fig.update_layout(title=label, xaxis_title="Year", yaxis_title=label)
        st.plotly_chart(fig, use_container_width=True)

        st.download_button(f"📥 Download {label} CSV", pivot_df.to_csv().encode('utf-8'), file_name=f"{label.replace(' ', '_')}_worldbank.csv")
    except Exception as e:
        st.error(f"Failed to load World Bank data for {label}: {e}")

# --- GDP Tab ---
with tabs[1]: render_world_bank_chart("GDP (current US$)", indicator_map["GDP (current US$)"])

# --- Inflation Tab ---
with tabs[2]: render_world_bank_chart("Inflation (CPI %)", indicator_map["Inflation (CPI %)"])

# --- Unemployment Tab ---
with tabs[3]: render_world_bank_chart("Unemployment Rate (%)", indicator_map["Unemployment Rate (%)"])

# --- CO2 Tab with Dropdown ---
with tabs[4]:
    selected_co2 = st.multiselect("Select CO₂ Indicators", options=list(co2_indicators.keys()), default=["CO₂ - Total Energy"])

    for co2_label in selected_co2:
        code = co2_indicators[co2_label]
        render_world_bank_chart(co2_label, code)
