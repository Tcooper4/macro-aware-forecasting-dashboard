import pandas as pd
from arch import arch_model

def forecast_garch(df, forecast_days=5):
    returns = 100 * df["Close"].pct_change().dropna()

    model = arch_model(returns, vol='Garch', p=1, q=1)
    fitted_model = model.fit(disp="off")

    forecast = fitted_model.forecast(horizon=forecast_days)
    mean_forecast = forecast.mean.iloc[-1].values[-1]  # scalar value

    current_price = df["Close"].iloc[-1]

    # Use percentage return to determine direction
    if mean_forecast > 0:
        return "BUY"
    elif mean_forecast < 0:
        return "SELL"
    else:
        return "HOLD"
