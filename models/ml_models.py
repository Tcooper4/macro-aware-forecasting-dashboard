from sklearn.ensemble import GradientBoostingRegressor
import numpy as np

def forecast_ml(prices, horizon=5):
    X, y = [], []
    for i in range(30, len(prices) - horizon):
        X.append(prices.iloc[i - 30:i].values)
        y.append((prices.iloc[i + horizon] - prices.iloc[i]) / prices.iloc[i])
    X, y = np.array(X), np.array(y)

    if len(X) == 0:
        return 0.0

    model = GradientBoostingRegressor()
    model.fit(X, y)

    latest = prices.iloc[-30:].values.reshape(1, -1)
    return model.predict(latest)[0]
