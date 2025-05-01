import pandas as pd
from utils.helpers import fetch_price_data
from models.ensemble import generate_forecast_ensemble
import datetime

tickers = ["AAPL", "MSFT", "SPY"]
today = datetime.date.today()
start = today - pd.DateOffset(years=5)

for ticker in tickers:
    df = fetch_price_data(ticker, start, today)
    result = generate_forecast_ensemble(df)
    result["forecast_table"].to_csv(f"forecasts/{ticker}_{today}.csv", index=False)
