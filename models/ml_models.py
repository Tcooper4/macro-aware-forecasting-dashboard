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
