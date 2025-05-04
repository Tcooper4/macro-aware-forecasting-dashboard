from hmmlearn.hmm import GaussianHMM
import numpy as np

def forecast_hmm(prices, horizon=5):
    returns = prices.pct_change().dropna().values.reshape(-1, 1)
    model = GaussianHMM(n_components=2, covariance_type="full", n_iter=100)
    model.fit(returns)
    hidden_states = model.predict(returns)
    current_state = hidden_states[-1]
    state_returns = returns[hidden_states == current_state]
    avg_return = np.mean(state_returns) * horizon
    return float(avg_return)
