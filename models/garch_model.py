from arch import arch_model

def forecast_garch(series, steps=5):
    returns = series.pct_change().dropna() * 100
    model = arch_model(returns, vol='Garch', p=1, q=1)
    model_fit = model.fit(disp="off")
    forecast = model_fit.forecast(horizon=steps)
    return forecast.variance.values[-1]
