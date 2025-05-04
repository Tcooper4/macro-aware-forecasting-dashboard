import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from utils.helpers import preprocess_for_model, generate_signal_from_return

def forecast_lstm(ticker, data, forecast_steps=5):
    try:
        series = preprocess_for_model(data, ticker, column='Close')

        if len(series) < 60:
            print(f"⚠️ Not enough data to fit LSTM for {ticker}.")
            return None, 'HOLD'

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(series.values.reshape(-1, 1))

        X, y = [], []
        window = 10
        for i in range(len(scaled) - window):
            X.append(scaled[i:i + window])
            y.append(scaled[i + window])
        X, y = np.array(X), np.array(y)

        model = Sequential()
        model.add(LSTM(units=50, input_shape=(X.shape[1], 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X, y, epochs=5, batch_size=16, verbose=0)

        last_input = scaled[-window:].reshape(1, window, 1)
        preds = []
        for _ in range(forecast_steps):
            pred = model.predict(last_input, verbose=0)
            preds.append(pred[0, 0])
            last_input = np.append(last_input[:, 1:, :], [[pred]], axis=1)

        preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1))
        returns = (preds[-1] - series.iloc[-1]) / series.iloc[-1]
        signal = generate_signal_from_return(returns)

        print(f"✅ LSTM signal for {ticker}: {signal} (Predicted return: {returns:.4f})")
        return returns, signal

    except Exception as e:
        print(f"❌ LSTM failed for {ticker}: {e}")
        return None, 'HOLD'
