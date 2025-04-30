import streamlit as st
import pandas_datareader.data as web
import plotly.graph_objects as go
import datetime
import wbdata
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="Macroeconomic Charts", layout="wide")
st.title("🌐 Live Macroeconomic Charts")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("📈 FRED Indicator")
    fred_series = st.selectbox("Choose FRED Series", [
        "FEDFUNDS",  # Federal Funds Rate
        "CPIAUCSL",  # Consumer Price Index
        "UNRATE",    # Unemployment Rate
        "GDPC1"      # Real GDP
    ])
    fred_label_map = {
        "FEDFUNDS": "Federal Funds Rate",
        "CPIAUCSL": "Consumer Price Index",
        "UNRATE": "Unemployment Rate",
        "GDPC1": "Real GDP"
    }

    st.markdown("---")
    st.subheader("🌍 World Bank GDP Comparison")

    # Get list of all valid countries from World Bank (exclude aggregates)
    all_countries = wbdata.get_countries()
    country_dict = {
        c['name']: c['id']
        for c in all_countries
        if c['region']['id'] != 'NA'  # exclude aggregates
    }

    selected_countries = st.multiselect(
        "Select Countries",
        options=sorted(country_dict.keys()),
        default=["United States", "Germany"]
    )

    indicator_code = "NY.GDP.MKTP.CD"  # GDP (current US$)
    indicator_name = "GDP (USD)"

# --- Date range ---
start = datetime.datetime(2000, 1, 1)
end = datetime.datetime.today()

# --- FRED Line Chart ---
try:
    st.subheader(f"📊 {fred_label_map[fred_series]} Over Time (FRED)")
    fred_data = web.DataReader(fred_series, "fred", start, end)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=fred_data.index,
        y=fred_data[fred_series],
        mode='lines',
        name=fred_label_map[fred_series]
    ))

    # Recession annotation (2008–2009)
    fig1.add_vrect(
        x0="2008-09-01", x1="2009-06-30",
        fillcolor="red", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="2008 Recession", annotation_position="top left"
    )

    fig1.update_layout(
        title=fred_label_map[fred_series],
        xaxis_title="Date",
        yaxis_title="Value",
        height=500
    )
    st.plotly_chart(fig1, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load FRED data: {e}")

# --- World Bank GDP Comparison ---
# --- World Bank GDP Comparison ---
try:
    st.subheader("🌐 GDP Comparison Between Countries")

    selected_iso = [country_dict[c] for c in selected_countries]
    raw_df = wbdata.get_dataframe({indicator_code: indicator_name}, country=selected_iso).reset_index()

    # Handle single-country case where 'country' column is missing
    if 'country' not in raw_df.columns and len(selected_countries) == 1:
        raw_df['country'] = selected_countries[0]

    # Convert 'date' to datetime
    raw_df['date'] = pd.to_datetime(raw_df['date'], format='%Y')

    # Filter by range
    filtered_df = raw_df[(raw_df['date'] >= start) & (raw_df['date'] <= end)]

    # Pivot for plotting
    pivot_df = filtered_df.pivot(index='date', columns='country', values=indicator_name)

    # Plot
    fig2 = go.Figure()
    for country in pivot_df.columns:
        fig2.add_trace(go.Scatter(
            x=pivot_df.index,
            y=pivot_df[country],
            mode='lines',
            name=country
        ))

    fig2.update_layout(
        title="GDP Comparison (World Bank)",
        xaxis_title="Year",
        yaxis_title="GDP (USD)",
        height=500
    )
    st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load World Bank data: {e}")
