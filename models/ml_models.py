import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def forecast_ml(df, steps):
    df["Return"] = df["Close"].pct_change()
    df["Lag1"] = df["Return"].shift(1)
    df["Lag2"] = df["Return"].shift(2)
    df.dropna(inplace=True)

    if len(df) < 30:
        return pd.Series([df["Close"].iloc[-1]] * steps)

    X = df[["Lag1", "Lag2"]]
    y = df["Return"]
    model = RandomForestRegressor()
    model.fit(X, y)

    preds, l1, l2 = [], X.iloc[-1, 0], X.iloc[-1, 1]
    for _ in range(steps):
        pred = model.predict([[l1, l2]])[0]
        preds.append(pred)
        l2, l1 = l1, pred

    base = df["Close"].iloc[-1]
    prices = [base * (1 + preds[0])]
    for i in range(1, steps):
        prices.append(prices[-1] * (1 + preds[i]))
    return pd.Series(prices)
