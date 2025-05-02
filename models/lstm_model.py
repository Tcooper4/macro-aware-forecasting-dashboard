import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from utils.expert import get_expert_settings
import tensorflow.keras.backend as K

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

    settings = get_expert_settings()
    units = settings.get("lstm", {}).get("units", 50)
    epochs = settings.get("lstm", {}).get("epochs", 5)

    # 💡 Fix: Reset session to avoid stack corruption in streamlit / re-runs
    K.clear_session()

    model = Sequential([
        LSTM(units, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(units),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)

    seq = scaled[-60:]
    preds = []
    for _ in range(steps):
        pred = model.predict(seq.reshape(1, 60, 1), verbose=0)
        preds.append(pred[0][0])
        seq = np.vstack([seq[1:], pred])

    forecast = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
    return pd.Series(forecast)
