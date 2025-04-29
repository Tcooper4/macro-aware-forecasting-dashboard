import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred
import streamlit as st
import os
from dotenv import load_dotenv

# --- Load FRED API Key from .env ---
load_dotenv()
fred_api_key = os.getenv("FRED_API_KEY")
fred = Fred(api_key=fred_api_key)

# --- Cached Fetch for Single Series ---
@st.cache_data
def fetch_and_plot_cached(series_id, label):
    """Fetches a single FRED series and returns it as a DataFrame with monthly frequency."""
    try:
        data = fred.get_series(series_id)
        df = pd.DataFrame(data, columns=[label])
        df = df.asfreq('MS')  # Monthly frequency
        return df
    except Exception as e:
        st.error(f"Error fetching {label} ({series_id}): {e}")
        return pd.DataFrame()

# --- Fetch Multiple Macroeconomic Indicators ---
@st.cache_data
def get_macro_indicators():
    """Retrieves multiple key macro indicators and returns a DataFrame."""
    series = {
        "Consumer Price Index (CPI)": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
        "Federal Funds Rate": "FEDFUNDS",
        "Real GDP": "GDPC1"
    }

    data = {}
    for label, code in series.items():
        try:
            data[label] = fred.get_series(code)
        except Exception as e:
            st.warning(f"Failed to fetch {label}: {e}")
            data[label] = pd.Series()

    df = pd.DataFrame(data)

    # Optional: Interpolate quarterly GDP to monthly
    if "Real GDP" in df.columns:
        df["Real GDP"] = df["Real GDP"].interpolate(method="linear")

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df
