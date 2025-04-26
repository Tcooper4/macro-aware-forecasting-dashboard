# src/fred_macro_data.py

import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

def fetch_and_plot(series_code: str, label: str) -> pd.Series:
    """
    Fetch real macroeconomic indicator data from FRED.
    """
    data = fred.get_series(series_code)
    data.name = label
    return data

def get_macro_indicators() -> pd.DataFrame:
    """
    Fetch real macroeconomic indicators (CPI, GDP, Unemployment, Fed Funds Rate).
    """
    indicators = {
        "CPIAUCSL": "CPI",
        "GDPC1": "Real GDP",
        "UNRATE": "Unemployment Rate",
        "FEDFUNDS": "Fed Funds Rate"
    }
    
    frames = []
    for code, label in indicators.items():
        series = fred.get_series(code)
        series.name = label
        frames.append(series)
    
    combined = pd.concat(frames, axis=1)
    return combined
