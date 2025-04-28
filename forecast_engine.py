import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

import pandas as pd

# Exponential Smoothing (Simple)
def forecast_prices_smoothing(series, forecast_days=5):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    series = series.dropna().astype(float)
    model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
    fitted = model.fit()
    forecast = fitted.forecast(forecast_days)
    return forecast

# ARIMA (Intermediate)
def forecast_prices_arima(series, forecast_days=5):
    from statsmodels.tsa.arima.model import ARIMA
    series = series.dropna().astype(float)
    model = ARIMA(series, order=(5,1,0))  # (p=5, d=1, q=0)
    fitted = model.fit()
    forecast = fitted.forecast(steps=forecast_days)
    return forecast

# Prophet (Advanced)
def forecast_prices_prophet(series, forecast_days=5):
    from prophet import Prophet
    df = series.dropna().astype(float).reset_index()
    df.columns = ['ds', 'y']

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)

    forecasted = forecast[['ds', 'yhat']].set_index('ds').iloc[-forecast_days:]['yhat']
    return forecasted

# SARIMA (Expert)
def forecast_prices_sarima(series, forecast_days=5):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    series = series.dropna().astype(float)
    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 0, 12))
    fitted = model.fit(disp=False)
    forecast = fitted.forecast(steps=forecast_days)
    return forecast

# LSTM Neural Net (Elite)
def forecast_prices_lstm(series, forecast_days=5):
    import numpy as np
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    from sklearn.preprocessing import MinMaxScaler

    series = series.dropna().astype(float)
    data = series.values.reshape(-1, 1)

    # Normalize
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Create sequences
    sequence_length = 60
    X, y = [], []
    for i in range(len(data_scaled) - sequence_length):
        X.append(data_scaled[i:i+sequence_length])
        y.append(data_scaled[i+sequence_length])
    X, y = np.array(X), np.array(y)

    # Build model
    model = keras.Sequential([
        layers.LSTM(50, activation='relu', input_shape=(sequence_length, 1)),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, verbose=0)

    # Forecast
    last_seq = data_scaled[-sequence_length:]
    forecast = []
    input_seq = last_seq.reshape((1, sequence_length, 1))

    for _ in range(forecast_days):
        next_pred = model.predict(input_seq, verbose=0)[0, 0]
        forecast.append(next_pred)
        input_seq = np.append(input_seq[:, 1:, :], [[[next_pred]]], axis=1)

    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1)).flatten()
    forecast_dates = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='B')

    return pd.Series(forecast, index=forecast_dates)
