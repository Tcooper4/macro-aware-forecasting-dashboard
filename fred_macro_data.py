import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

@st.cache_data
def fetch_and_plot_cached(series_id, label):
    data = fred.get_series(series_id)
    df = pd.DataFrame(data, columns=[label])
    df = df.asfreq('MS')  # Month Start frequency for macro data
    return df

@st.cache_data
def get_macro_indicators():
    series = {
        "CPI": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
        "Fed Funds Rate": "FEDFUNDS",
        "Real GDP": "GDPC1"
    }
    data = {}
    for label, code in series.items():
        data[label] = fred.get_series(code)
    df = pd.DataFrame(data)
    df = df.asfreq('MS')  # Month Start frequency for macro indicators
    return df
