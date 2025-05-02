import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from utils.expert import get_expert_settings

def forecast_hmm(df, steps):
    returns = np.log(df["Close"] / df["Close"].shift(1)).dropna().values.reshape(-1, 1)
    if len(returns) < 30:
        return pd.Series([df["Close"].iloc[-1]] * steps)

    settings = get_expert_settings()
    n_states = settings.get("hmm_states", 2)

    try:
        model = GaussianHMM(n_components=n_states, covariance_type="diag", n_iter=1000)
        model.fit(returns)
        simulated, _ = model.sample(steps)
        base = df["Close"].iloc[-1]
        return pd.Series([base * np.exp(simulated[:i].sum()) for i in range(1, steps + 1)])
    except:
        return pd.Series([df["Close"].iloc[-1]] * steps)
