import streamlit as st
import pandas_datareader.data as web
import plotly.graph_objects as go
import datetime
import wbdata
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="Macroeconomic Charts", layout="wide")
st.title("🌐 Live Macroeconomic Charts")

# --- Sidebar: Theme and Inputs ---
with st.sidebar:
    st.header("⚙️ Settings")

    theme = st.selectbox("Select Chart Theme", ["Light", "Dark"])
    template = "plotly_dark" if theme == "Dark" else "plotly_white"

    st.markdown("---")
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
    st.subheader("🌍 World Bank Comparison")
    country_options = {"United States": "US", "Germany": "DE", "China": "CN", "Japan": "JP"}
    selected_countries = st.multiselect("Select Countries", options=list(country_options.keys()), default=["United States", "Germany"])
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
    fig1.add_trace(go.Scatter(x=fred_data.index, y=fred_data[fred_series],
                              mode='lines', name=fred_label_map[fred_series]))
    fig1.update_layout(title=fred_label_map[fred_series],
                       xaxis_title="Date", yaxis_title="Value", template=template)

    # --- Recession Highlight Example (2008–2009) ---
    fig1.add_vrect(x0="2008-09-01", x1="2009-06-30", fillcolor="red", opacity=0.2,
                   layer="below", line_width=0,
                   annotation_text="2008 Recession", annotation_position="top left")

    st.plotly_chart(fig1, use_container_width=True)
except Exception as e:
    st.error(f"Failed to load FRED data: {e}")

# --- World Bank GDP Comparison ---
try:
    st.subheader("🌐 GDP Comparison Between Countries")

    selected_iso = [country_options[c] for c in selected_countries]

    # Get raw WB data (no convert_date or data_date support in latest versions)
    raw_df = wbdata.get_dataframe({indicator_code: indicator_name}, country=selected_iso)
    raw_df = raw_df.reset_index()

    # Convert year to datetime
    raw_df['date'] = pd.to_datetime(raw_df['date'], format='%Y')

    # Filter by range
    filtered_df = raw_df[(raw_df['date'] >= start) & (raw_df['date'] <= end)]

    # Pivot for plotting
    pivot_df = filtered_df.pivot(index='date', columns='country', values=indicator_name)

    fig2 = go.Figure()
    for country in pivot_df.columns:
        fig2.add_trace(go.Scatter(x=pivot_df.index, y=pivot_df[country],
                                  mode='lines', name=country))

    fig2.update_layout(title="GDP Comparison (World Bank)",
                       xaxis_title="Year", yaxis_title="GDP (USD)",
                       template=template)
    st.plotly_chart(fig2, use_container_width=True)
except Exception as e:
    st.error(f"Failed to load World Bank data: {e}")
