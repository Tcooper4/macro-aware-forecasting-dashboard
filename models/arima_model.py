from statsmodels.tsa.arima.model import ARIMA

def forecast_arima(prices, horizon=5):
    model = ARIMA(prices, order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=horizon)
    return (forecast[-1] - prices.iloc[-1]) / prices.iloc[-1]
