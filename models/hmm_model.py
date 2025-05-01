import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

def forecast_hmm(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    returns = np.log(df["Close"] / df["Close"].shift(1)).dropna().values.reshape(-1, 1)
    model = GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
    model.fit(returns)
    sampled_returns, _ = model.sample(steps)
    last_price = df["Close"].iloc[-1]
    prices = [last_price * np.exp(sampled_returns[:i].sum()) for i in range(1, steps + 1)]
    return pd.Series(prices)
