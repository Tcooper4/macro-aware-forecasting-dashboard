import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from utils.helpers import fetch_price_data, preprocess_for_model, generate_signal_from_return

def forecast_arima(ticker, data, forecast_steps=5):
    """
    Fit ARIMA to historical close prices and forecast future returns.
    Returns the forecasted return and trading signal.
    """
    try:
        # Preprocess to extract ('Close', ticker) series
        series = preprocess_for_model(data, ticker, column='Close')

        if len(series) < 30:
            print(f"⚠️ Not enough data to fit ARIMA for {ticker}.")
            return None, 'HOLD'

        # Difference the series to make it stationary
        diff_series = series.diff().dropna()

        # Fit ARIMA model (p,d,q) – simple auto choice here; you can optimize later
        model = ARIMA(diff_series, order=(1, 0, 1))
        model_fit = model.fit()

        # Forecast differenced values
        forecast = model_fit.forecast(steps=forecast_steps)
        total_forecast_return = forecast.sum()

        # Convert forecasted return into a trading signal
        signal = generate_signal_from_return(total_forecast_return)

        print(f"✅ ARIMA signal for {ticker}: {signal} (Predicted return: {total_forecast_return:.4f})")
        return total_forecast_return, signal

    except Exception as e:
        print(f"❌ ARIMA failed for {ticker}: {e}")
        return None, 'HOLD'
