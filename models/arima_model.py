import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from utils.helpers import fetch_price_data
from utils.expert import get_expert_settings


def forecast_arima(df, steps):
    close = df["Close"].dropna()
    if close.empty or len(close) < 30:
        return pd.Series([close.iloc[-1]] * steps if not close.empty else [100] * steps)

    settings = get_expert_settings()
    p, d, q = settings.get("arima_order", (5, 1, 0))

    try:
        model = ARIMA(close, order=(p, d, q)).fit()
        return model.forecast(steps).reset_index(drop=True)
    except:
        return pd.Series([close.iloc[-1]] * steps)
