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

# --- Multi-Country GDP Comparison ---
try:
    st.subheader(f"🌐 GDP Comparison Between Countries")

    selected_iso = [country_options[c] for c in selected_countries]
    wb_df = wbdata.get_dataframe({indicator_code: indicator_name}, country=selected_iso,
                                 data_date=(start, end), convert_date=True).unstack(level=0)

    wb_df = wb_df[indicator_name]
    wb_df.index.name = "Date"
    wb_df.sort_index(inplace=True)

    fig2 = go.Figure()
    for country in wb_df.columns:
        fig2.add_trace(go.Scatter(x=wb_df.index, y=wb_df[country], mode='lines', name=country))

    fig2.update_layout(title="GDP Comparison", xaxis_title="Date", yaxis_title="USD", template=template)
    st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load World Bank data: {e}")
