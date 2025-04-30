import streamlit as st
import pandas_datareader.data as web
import plotly.graph_objects as go
import datetime
import wbdata
import pandas as pd
from io import StringIO

# --- Page config ---
st.set_page_config(page_title="Macroeconomic Charts", layout="wide")
st.title("🌐 Live Macroeconomic Charts")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("FRED Indicator")
    fred_series = st.selectbox("Choose FRED Series", [
        "FEDFUNDS", "CPIAUCSL", "UNRATE", "GDPC1"
    ])
    fred_label_map = {
        "FEDFUNDS": "Federal Funds Rate",
        "CPIAUCSL": "Consumer Price Index",
        "UNRATE": "Unemployment Rate",
        "GDPC1": "Real GDP"
    }

    st.markdown("---")
    st.subheader("World Bank Settings")

    all_countries = wbdata.get_countries()
    country_dict = {
        c['name']: c['id'] for c in all_countries if c['region']['id'] != 'NA'
    }
    selected_countries = st.multiselect(
        "Select Countries",
        options=sorted(country_dict.keys()),
        default=["United States", "Germany"]
    )

    indicator_map = {
        "GDP (current US$)": "NY.GDP.MKTP.CD",
        "Inflation (CPI %)": "FP.CPI.TOTL.ZG",
        "Unemployment Rate (%)": "SL.UEM.TOTL.ZS",
        "CO₂ Emissions (metric tons/capita)": "EN.ATM.CO2E.PC"
    }
    selected_indicator = st.selectbox("World Bank Indicator", list(indicator_map.keys()))

    st.markdown("---")
    start_year = st.slider("Start Year", min_value=1960, max_value=2022, value=2000)
    end_year = st.slider("End Year", min_value=1960, max_value=2023, value=2023)

    refresh = st.button("🔄 Refresh Data")

# --- Date Range ---
start = datetime.datetime(start_year, 1, 1)
end = datetime.datetime(end_year, 12, 31)

# --- Tabs Layout ---
tab1, tab2 = st.tabs(["📈 FRED Charts", "🌍 World Bank Indicators"])

# --- Tab 1: FRED Data ---
with tab1:
    try:
        st.subheader(f"{fred_label_map[fred_series]} Over Time (FRED)")
        fred_data = web.DataReader(fred_series, "fred", start, end)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fred_data.index,
            y=fred_data[fred_series],
            mode='lines',
            name=fred_label_map[fred_series]
        ))

        fig.add_vrect(
            x0="2008-09-01", x1="2009-06-30",
            fillcolor="red", opacity=0.2,
            layer="below", line_width=0,
            annotation_text="2008 Recession", annotation_position="top left"
        )

        fig.update_layout(
            title=fred_label_map[fred_series],
            xaxis_title="Date",
            yaxis_title="Value",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        csv_fred = fred_data.to_csv().encode("utf-8")
        st.download_button("📥 Download FRED Data (CSV)", csv_fred, file_name=f"{fred_series}_fred.csv")
    except Exception as e:
        st.error(f"Failed to load FRED data: {e}")

# --- Tab 2: World Bank Data ---
with tab2:
    try:
        st.subheader(f"{selected_indicator} Between {start_year} and {end_year}")

        indicator_code = indicator_map[selected_indicator]
        selected_iso = [country_dict[c] for c in selected_countries]
        raw_df = wbdata.get_dataframe({indicator_code: selected_indicator}, country=selected_iso).reset_index()

        # Handle single-country shape
        if 'country' not in raw_df.columns and len(selected_countries) == 1:
            raw_df['country'] = selected_countries[0]

        raw_df['date'] = pd.to_datetime(raw_df['date'], format='%Y')
        filtered_df = raw_df[(raw_df['date'] >= start) & (raw_df['date'] <= end)]
        pivot_df = filtered_df.pivot(index='date', columns='country', values=selected_indicator)

        fig = go.Figure()
        for country in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df[country],
                mode='lines',
                name=country
            ))

        fig.update_layout(
            title=f"{selected_indicator} (World Bank)",
            xaxis_title="Year",
            yaxis_title=selected_indicator,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Download button
        csv_wb = pivot_df.to_csv().encode("utf-8")
        st.download_button(f"📥 Download {selected_indicator} Data (CSV)", csv_wb,
                           file_name=f"{selected_indicator.replace(' ', '_')}_worldbank.csv")
    except Exception as e:
        st.error(f"Failed to load World Bank data: {e}")
