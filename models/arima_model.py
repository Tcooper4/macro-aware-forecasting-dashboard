import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from utils.common import fetch_price_data, preprocess_for_model, generate_signal_from_return

def forecast_arima(ticker, data, forecast_steps=5):
    try:
        series = preprocess_for_model(data, ticker, column='Close')

        if len(series) < 30:
            print(f"⚠️ Not enough data to fit ARIMA for {ticker}.")
            return None, 'HOLD'

        diff_series = series.diff().dropna()
        model = ARIMA(diff_series, order=(1, 0, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=forecast_steps)
        total_forecast_return = forecast.sum()

        signal = generate_signal_from_return(total_forecast_return)

        print(f"✅ ARIMA signal for {ticker}: {signal} (Predicted return: {total_forecast_return:.4f})")
        return total_forecast_return, signal, abs(total_forecast_return)

    except Exception as e:
        print(f"❌ ARIMA failed for {ticker}: {e}")
        return None, 'HOLD'
