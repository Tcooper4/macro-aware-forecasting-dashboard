import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def forecast_lstm(df, steps):
    data = df["Close"].values.reshape(-1, 1)
    if len(data) < 100:
        return pd.Series([data[-1][0]] * steps)

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

    seq = scaled[-60:]
    preds = []
    for _ in range(steps):
        pred = model.predict(seq.reshape(1, 60, 1), verbose=0)
        preds.append(pred[0][0])
        seq = np.vstack([seq[1:], pred])

    forecast = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
    return pd.Series(forecast)
