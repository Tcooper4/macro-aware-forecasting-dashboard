def forecast_lstm(ticker, df, forecast_days=5):
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, LSTM
    import pandas as pd

    data = df[["Close"]].copy()
    data.dropna(inplace=True)
    values = data.values

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(values)

    # Prepare training data
    X_train, y_train = [], []
    look_back = 60
    for i in range(look_back, len(scaled_data) - forecast_days):
        X_train.append(scaled_data[i - look_back:i, 0])
        y_train.append(scaled_data[i + forecast_days - 1, 0])
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Build LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=(X_train.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")

    model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=0)

    # Forecast
    last_60 = scaled_data[-look_back:]
    X_input = np.reshape(last_60, (1, look_back, 1))
    forecast = model.predict(X_input)

    # ✅ Extract scalar value safely
    forecast_value = float(forecast.flatten()[0])

    # ✅ Calculate percentage change from last actual
    last_real_price = values[-1][0]
    predicted_price = scaler.inverse_transform([[forecast_value]])[0][0]
    pct_return = (predicted_price - last_real_price) / last_real_price

    signal = "BUY" if pct_return > 0.01 else "SELL" if pct_return < -0.01 else "HOLD"
    return pct_return, signal
