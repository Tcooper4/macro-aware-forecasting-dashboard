import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def forecast_ml(df, forecast_days=5):
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df['Lag1'] = df['Return'].shift(1)
    df['Lag2'] = df['Return'].shift(2)
    df.dropna(inplace=True)

    X = df[['Lag1', 'Lag2']]
    y = df['Return']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

    model = XGBRegressor(n_estimators=100, max_depth=3)
    model.fit(X_train, y_train)

    latest_features = scaler.transform([X.iloc[-1].values])  # shape: (1, 2)
    prediction = model.predict(latest_features)[0]  # scalar

    if prediction > 0:
        return "BUY"
    elif prediction < 0:
        return "SELL"
    else:
        return "HOLD"

def audit_ml_accuracy(df, forecast_days=5, test_size=0.2):
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.ensemble import RandomForestRegressor
    import numpy as np

    df = df.copy()
    df["return"] = df["Close"].pct_change()
    df["target"] = df["Close"].shift(-forecast_days)
    df = df.dropna()

    features = df[["Close", "return"]]
    target = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=test_size, shuffle=False)

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    direction_accuracy = np.mean(np.sign(y_pred[1:] - y_pred[:-1]) == np.sign(y_test[1:] - y_test[:-1]))

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "directional_accuracy": round(direction_accuracy, 4)
    }
