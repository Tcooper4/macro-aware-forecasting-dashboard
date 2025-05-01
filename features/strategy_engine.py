import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from hmmlearn.hmm import GaussianHMM

def calculate_indicators(df):
    df = df.copy()

    # --- RSI ---
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # --- MACD ---
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # --- EMA Crossover ---
    df["EMA_Fast"] = df["Close"].ewm(span=8, adjust=False).mean()
    df["EMA_Slow"] = df["Close"].ewm(span=21, adjust=False).mean()

    return df.dropna()

def arima_trend(df, steps=5):
    series = df["Close"].dropna()
    model = ARIMA(series, order=(1, 1, 1))
    fit = model.fit()
    forecast = fit.forecast(steps=steps)
    return forecast.mean() > series.iloc[-1]

def garch_volatility(df):
    returns = 100 * df["Close"].pct_change().dropna()
    model = arch_model(returns, vol="Garch", p=1, q=1)
    fit = model.fit(disp="off")
    return fit.conditional_volatility.iloc[-1]

def hmm_regime(df, n_states=3):
    log_returns = np.log(df["Close"] / df["Close"].shift(1)).dropna().values.reshape(-1, 1)
    model = GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)
    model.fit(log_returns)
    return model.predict(log_returns)[-1]

def generate_signal(df):
    votes = []

    # RSI vote
    rsi = df["RSI"].iloc[-1]
    if rsi < 30:
        votes.append("BUY")
    elif rsi > 70:
        votes.append("SELL")

    # MACD crossover vote
    if df["MACD"].iloc[-1] > df["MACD_Signal"].iloc[-1] and df["MACD"].iloc[-2] <= df["MACD_Signal"].iloc[-2]:
        votes.append("BUY")
    elif df["MACD"].iloc[-1] < df["MACD_Signal"].iloc[-1] and df["MACD"].iloc[-2] >= df["MACD_Signal"].iloc[-2]:
        votes.append("SELL")

    # EMA crossover
    if df["EMA_Fast"].iloc[-1] > df["EMA_Slow"].iloc[-1]:
        votes.append("BUY")
    else:
        votes.append("SELL")

    # ARIMA trend
    if arima_trend(df):
        votes.append("BUY")
    else:
        votes.append("SELL")

    # HMM regime
    regime = hmm_regime(df)
    if regime == 0:
        votes.append("BUY")
    elif regime == 2:
        votes.append("SELL")
    else:
        votes.append("HOLD")

    # Tally the votes
    buy_votes = votes.count("BUY")
    sell_votes = votes.count("SELL")
    score = buy_votes - sell_votes

    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    # Volatility and position size
    volatility = garch_volatility(df)
    position_size = max(0.1, min(1.0, 1 / (volatility / 10)))

    return {
        "Signal": signal,
        "Score": score,
        "Volatility": round(volatility, 2),
        "Position Size": round(position_size, 2),
        "Votes": votes
    }
