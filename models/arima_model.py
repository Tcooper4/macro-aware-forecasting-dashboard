from statsmodels.tsa.arima.model import ARIMA

def forecast_arima(series, steps=5):
    model = ARIMA(series, order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    return forecast
