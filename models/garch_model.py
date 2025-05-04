from arch import arch_model

def forecast_garch(prices, horizon=5):
    returns = prices.pct_change().dropna() * 100
    model = arch_model(returns, vol="GARCH", p=1, q=1)
    model_fit = model.fit(disp="off")
    forecast = model_fit.forecast(horizon=horizon)
    forecast_return = forecast.mean.iloc[-1].mean() / 100
    return forecast_return
