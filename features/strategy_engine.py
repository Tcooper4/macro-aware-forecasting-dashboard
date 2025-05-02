def apply_strategy_settings(forecast_df, user_settings):
    """
    Generate strategy suggestion from forecast + user input.
    """
    signal = forecast_df["Final Signal"].iloc[-1]

    size_map = {
        "Low": 0.2,
        "Medium": 0.5,
        "High": 1.0
    }
    size_factor = size_map.get(user_settings.get("risk_tolerance", "Medium"), 0.5)
    dynamic = user_settings.get("position_sizing") == "Dynamic"
    position = round(size_factor * 100 if dynamic else 100, 2)

    return {
        "action": signal,
        "position_size": position,
        "frequency": user_settings.get("trade_frequency", "Weekly")
    }
