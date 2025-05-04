import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from arch import arch_model
from utils.expert import get_expert_settings
from utils.common import fetch_price_data

def forecast_garch(df, steps):
    returns = df["Close"].pct_change().dropna() * 100
    if len(returns) < 30:
        return pd.Series([df["Close"].iloc[-1]] * steps)

    settings = get_expert_settings()
    p, q = settings.get("garch_order", (1, 1))

    try:
        model = arch_model(returns, vol='Garch', p=p, q=q)
        res = model.fit(disp="off")
        mean = res.forecast(horizon=steps).mean.iloc[-1].values / 100
        base = df["Close"].iloc[-1]
        return pd.Series([base * (1 + mean[0])**i for i in range(1, steps + 1)])
    except:
        return pd.Series([df["Close"].iloc[-1]] * steps)
