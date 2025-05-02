import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def forecast_arima(df, steps):
    close = df["Close"].dropna()
    if close.empty or len(close) < 30:
        return pd.Series([close.iloc[-1]] * steps if not close.empty else [100] * steps)

    try:
        model = ARIMA(close, order=(5,1,0)).fit()
        return model.forecast(steps).reset_index(drop=True)
    except:
        return pd.Series([close.iloc[-1]] * steps)
