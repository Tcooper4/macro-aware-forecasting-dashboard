import pandas as pd
from arch import arch_model

def forecast_garch(df, steps):
    returns = df["Close"].pct_change().dropna() * 100
    if len(returns) < 30:
        return pd.Series([df["Close"].iloc[-1]] * steps)

    try:
        model = arch_model(returns, vol='Garch', p=1, q=1)
        res = model.fit(disp="off")
        mean = res.forecast(horizon=steps).mean.iloc[-1].values / 100
        base = df["Close"].iloc[-1]
        prices = [base * (1 + mean[0]) ** i for i in range(1, steps + 1)]
        return pd.Series(prices)
    except:
        return pd.Series([df["Close"].iloc[-1]] * steps)
