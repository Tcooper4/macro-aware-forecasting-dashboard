from hmmlearn.hmm import GaussianHMM
import numpy as np

def detect_regimes(series, n_states=3):
    log_returns = np.log(series / series.shift(1)).dropna().values.reshape(-1, 1)
    model = GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)
    model.fit(log_returns)
    hidden_states = model.predict(log_returns)
    return hidden_states
