import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

def train_lstm(series, look_back=60, forecast_horizon=5):
    scaler = MinMaxScaler()
    scaled_series = scaler.fit_transform(series.values.reshape(-1, 1))

    X, y = [], []
    for i in range(look_back, len(scaled_series) - forecast_horizon):
        X.append(scaled_series[i - look_back:i])
        y.append(scaled_series[i:i + forecast_horizon].flatten())
    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(forecast_horizon))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)

    last_sequence = scaled_series[-look_back:].reshape(1, look_back, 1)
    prediction = model.predict(last_sequence)[0]
    return scaler.inverse_transform(prediction.reshape(-1, 1)).flatten()
