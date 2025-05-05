import json
import os

TUNING_FILE = "data/model_performance.json"

def load_model_weights():
    if not os.path.exists(TUNING_FILE):
        return {
            "ARIMA": 1.0,
            "GARCH": 1.0,
            "HMM": 1.0,
            "LSTM": 1.0,
            "XGBoost": 1.0
        }

    with open(TUNING_FILE, "r") as f:
        data = json.load(f)
        return data.get("weights", {})

def update_model_accuracy(model_name, is_correct):
    if not os.path.exists(TUNING_FILE):
        history = {"accuracies": {}, "weights": {}}
    else:
        with open(TUNING_FILE, "r") as f:
            history = json.load(f)

    history.setdefault("accuracies", {}).setdefault(model_name, {"correct": 0, "total": 0})
    record = history["accuracies"][model_name]
    record["total"] += 1
    if is_correct:
        record["correct"] += 1

    # Update weight
    accuracy = record["correct"] / max(1, record["total"])
    weight = round(0.5 + 1.5 * accuracy, 2)
    history.setdefault("weights", {})[model_name] = weight

    with open(TUNING_FILE, "w") as f:
        json.dump(history, f, indent=2)

def tune_model_weights():
    if not os.path.exists(TUNING_FILE):
        return load_model_weights()

    with open(TUNING_FILE, "r") as f:
        history = json.load(f)

    accuracies = history.get("accuracies", {})
    new_weights = {}
    for model, record in accuracies.items():
        accuracy = record["correct"] / max(1, record["total"])
        new_weights[model] = round(0.5 + 1.5 * accuracy, 2)

    history["weights"] = new_weights

    with open(TUNING_FILE, "w") as f:
        json.dump(history, f, indent=2)

    return new_weights
