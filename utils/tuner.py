# dynamic_tuning.py

import pandas as pd
import json
import os

# Path to model performance history
PERFORMANCE_LOG = "data/model_performance_log.csv"
TUNING_CONFIG = "config/model_weights.json"

# Default model weights (fallback)
def default_weights():
    return {
        "ARIMA": 1.0,
        "GARCH": 1.0,
        "HMM": 1.0,
        "LSTM": 1.0,
        "XGBoost": 1.0
    }

# Load historical performance log and compute new weights
def update_model_weights(forecast_df=None):
    if forecast_df is not None:
        # OPTIONAL: Write logic to update performance log from forecast_df
        pass  # Placeholder for future logging

    if not os.path.exists(PERFORMANCE_LOG):
        print("No performance log found. Using default weights.")
        return default_weights()

    df = pd.read_csv(PERFORMANCE_LOG)

    required_cols = {"Model", "Accuracy", "Sharpe", "Return"}
    if not required_cols.issubset(set(df.columns)):
        print("Performance log missing required columns. Using default weights.")
        return default_weights()

    df["score"] = 0.4 * df["Accuracy"] + 0.3 * df["Sharpe"] + 0.3 * df["Return"]
    total_score = df["score"].sum()
    weights = (df.groupby("Model")["score"].mean() / total_score).to_dict()

    with open(TUNING_CONFIG, "w") as f:
        json.dump(weights, f, indent=4)

    print("Updated model weights:", weights)
    return weights


# Load weights in other modules
def load_model_weights():
    if os.path.exists(TUNING_CONFIG):
        with open(TUNING_CONFIG, "r") as f:
            return json.load(f)
    return default_weights()

if __name__ == "__main__":
    update_model_weights()
