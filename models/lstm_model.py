import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def forecast_lstm(ticker, df, forecast_days=5, window_size=30):
    """
    Forecasts stock price using an LSTM model and returns signal (BUY/SELL/HOLD).
    """

    if "Close" not in df.columns:
        raise ValueError("DataFrame must contain 'Close' column")

    # === Prepare the data ===
    data = df["Close"].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    X, y = [], []
    for i in range(window_size, len(data_scaled) - forecast_days):
        X.append(data_scaled[i - window_size:i])
        y.append(data_scaled[i + forecast_days - 1])  # Predict price after `forecast_days`

    X = np.array(X)  # shape: (samples, timesteps, features)
    y = np.array(y).reshape(-1, 1)  # shape: (samples, 1)

    # === Split into train/test ===
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # === Build LSTM Model ===
    model = Sequential()
    model.add(LSTM(units=50, activation='relu', input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    # === Train the model ===
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)

    # === Predict ===
    last_sequence = data_scaled[-window_size:].reshape(1, window_size, 1)
    future_price_scaled = model.predict(last_sequence)[0][0]
    future_price = scaler.inverse_transform([[future_price_scaled]])[0][0]

    current_price = df["Close"].iloc[-1]
    predicted_return = (future_price - current_price) / current_price

    # === Signal logic ===
    if predicted_return > 0.02:
        signal = "BUY"
    elif predicted_return < -0.02:
        signal = "SELL"
    else:
        signal = "HOLD"

    print(f"✅ LSTM signal for {ticker}: {signal} (Predicted return: {predicted_return:.4f})")

    return predicted_return, signal

def audit_lstm_accuracy(ticker, df, forecast_days=5, test_size=0.2):
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    prices = df["Close"].values
    n_test = int(len(prices) * test_size)

    # Create sequences
    sequence_length = 30
    X, y = [], []
    for i in range(sequence_length, len(prices)):
        X.append(prices[i-sequence_length:i])
        y.append(prices[i])

    X, y = np.array(X), np.array(y)

    # Reshape for LSTM
    X = X.reshape((X.shape[0], X.shape[1], 1))

    X_train, X_test = X[:-n_test], X[-n_test:]
    y_train, y_test = y[:-n_test], y[-n_test:]

    model = build_lstm_model(input_shape=(X.shape[1], 1))
    model.fit(X_train, y_train, epochs=5, batch_size=16, verbose=0)

    y_pred = model.predict(X_test).flatten()

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    direction_accuracy = np.mean(np.sign(y_pred[1:] - y_pred[:-1]) == np.sign(y_test[1:] - y_test[:-1]))

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "directional_accuracy": round(direction_accuracy, 4),
        "ticker": ticker
    }
