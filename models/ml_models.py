import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def forecast_ml(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    df["Return"] = df["Close"].pct_change()
    df["Lag1"] = df["Return"].shift(1)
    df["Lag2"] = df["Return"].shift(2)
    df.dropna(inplace=True)
    
    X = df[["Lag1", "Lag2"]]
    y = df["Return"]

    model = RandomForestRegressor()
    model.fit(X, y)

    preds = []
    lag1, lag2 = X.iloc[-1].values
    for _ in range(steps):
        pred = model.predict([[lag1, lag2]])[0]
        preds.append(pred)
        lag2, lag1 = lag1, pred

    last_price = df["Close"].iloc[-1]
    prices = [last_price * (1 + preds[0])]
    for i in range(1, steps):
        prices.append(prices[-1] * (1 + preds[i]))
    return pd.Series(prices)
