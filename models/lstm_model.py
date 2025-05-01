import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def forecast_lstm(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    data = df["Close"].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    
    X, y = [], []
    for i in range(60, len(scaled)):
        X.append(scaled[i-60:i])
        y.append(scaled[i])
    X, y = np.array(X), np.array(y)
    
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    last_seq = scaled[-60:]
    preds = []
    for _ in range(steps):
        inp = last_seq.reshape(1, 60, 1)
        pred = model.predict(inp, verbose=0)
        preds.append(pred[0][0])
        last_seq = np.append(last_seq[1:], pred)

    forecast_scaled = np.array(preds).reshape(-1, 1)
    forecast = scaler.inverse_transform(forecast_scaled).flatten()
    return pd.Series(forecast)
