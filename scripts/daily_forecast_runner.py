import pandas as pd
from models.lstm_model import train_lstm
from features.strategy_engine import calculate_indicators, generate_signal
from models.ml_models import prepare_ml_data, predict_xgboost, predict_random_forest, predict_logistic
from models.ensemble import ensemble_vote
from datetime import date
import os

from alpha_vantage.timeseries import TimeSeries

def fetch_daily(ticker="SPY"):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    ts = TimeSeries(key=api_key, output_format="pandas")
    df, _ = ts.get_daily(symbol=ticker, outputsize="full")
    df = df.rename(columns={
        "4. close": "Close",
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "5. volume": "Volume"
    })
    df = df[["Close", "High", "Low", "Open", "Volume"]]
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df

def run_forecast():
    df = fetch_daily("SPY")
    df = calculate_indicators(df)
    X, y = prepare_ml_data(df)
    X_train, X_test = X[:-5], X[-5:]
    y_train = y[:-5]

    pred1, conf1 = predict_xgboost(X_train, y_train, X_test)
    pred2, conf2 = predict_random_forest(X_train, y_train, X_test)
    pred3, conf3 = predict_logistic(X_train, y_train, X_test)
    ensemble_signal, score = ensemble_vote([pred1, pred2, pred3], [conf1, conf2, conf3])

    lstm = train_lstm(df["Close"], forecast_horizon=5)

    summary = pd.DataFrame([{
        "Date": str(date.today()),
        "Signal": ensemble_signal,
        "Confidence": score,
        "Forecast_1d": lstm[0],
        "Forecast_5d": lstm[-1],
    }])
    summary.to_csv("forecast_log.csv", mode='a', index=False, header=not os.path.exists("forecast_log.csv"))

if __name__ == "__main__":
    run_forecast()
