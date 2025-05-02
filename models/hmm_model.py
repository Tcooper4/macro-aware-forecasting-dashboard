import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

def forecast_hmm(df, steps):
    returns = np.log(df["Close"] / df["Close"].shift(1)).dropna().values.reshape(-1, 1)
    if len(returns) < 30:
        return pd.Series([df["Close"].iloc[-1]] * steps)

    try:
        model = GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
        model.fit(returns)
        simulated, _ = model.sample(steps)
        base = df["Close"].iloc[-1]
        series = [base * np.exp(simulated[:i].sum()) for i in range(1, steps + 1)]
        return pd.Series(series)
    except:
        return pd.Series([df["Close"].iloc[-1]] * steps)
