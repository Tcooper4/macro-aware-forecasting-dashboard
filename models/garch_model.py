import pandas as pd
from arch import arch_model

def forecast_garch(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    returns = df["Close"].pct_change().dropna() * 100
    model = arch_model(returns, vol='Garch', p=1, q=1)
    res = model.fit(disp="off")
    forecast = res.forecast(horizon=steps)
    mean_forecast = forecast.mean.iloc[-1].values / 100
    last_price = df["Close"].iloc[-1]
    prices = [last_price * (1 + mean_forecast[0])**i for i in range(1, steps + 1)]
    return pd.Series(prices)
