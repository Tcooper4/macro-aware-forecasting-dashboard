def forecast_lstm(ticker, df, forecast_days=5):
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense

    # Ensure enough data
    if df.shape[0] < 100:
        return 0.0, "HOLD", 0.0

    data = df[["Close"]].copy().dropna()
    values = data.values
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(values)

    look_back = 60
    X, y = [], []

    for i in range(look_back, len(scaled_data) - forecast_days):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i + forecast_days - 1, 0])

    if len(X) == 0:
        return 0.0, "HOLD", 0.0

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=False, input_shape=(X.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    X_input = scaled_data[-look_back:]
    X_input = np.reshape(X_input, (1, look_back, 1))
    forecast = model.predict(X_input, verbose=0)
    forecast_value = float(forecast.flatten()[0])

    predicted_price = scaler.inverse_transform([[forecast_value]])[0][0]
    last_price = values[-1][0]
    pct_return = (predicted_price - last_price) / last_price
    signal = "BUY" if pct_return > 0.01 else "SELL" if pct_return < -0.01 else "HOLD"
    confidence = abs(pct_return)

    return pct_return, signal, confidence
