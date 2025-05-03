import pandas as pd
import requests
from io import StringIO

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch S&P 500 tickers from Wikipedia")

    # Use StringIO to suppress the FutureWarning
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    
    # Return a clean list of ticker strings
    return df["Symbol"].astype(str).str.replace(".", "-", regex=False).tolist()
