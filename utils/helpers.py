def aggregate_signals(predictions: dict) -> str:
    """
    Aggregates signals from multiple models and returns a final recommendation:
    'BUY', 'SELL', or 'HOLD'
    """
    buy_count = sum(1 for pred in predictions.values() if pred == "BUY")
    sell_count = sum(1 for pred in predictions.values() if pred == "SELL")

    if buy_count > sell_count:
        return "BUY"
    elif sell_count > buy_count:
        return "SELL"
    else:
        return "HOLD"
