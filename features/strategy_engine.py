def apply_strategy_settings(forecast_df, user_settings):
    """
    user_settings = {
        "risk_tolerance": "Low" | "Medium" | "High",
        "trade_frequency": "Daily" | "Weekly",
        "position_sizing": "Fixed" | "Dynamic"
    }
    """
    signal = forecast_df["Final Signal"].iloc[-1]
    
    sizing_map = {
        "Low": 0.2,
        "Medium": 0.5,
        "High": 1.0
    }

    size_factor = sizing_map.get(user_settings.get("risk_tolerance", "Medium"), 0.5)
    dynamic_adjustment = 1.0 if user_settings.get("position_sizing") == "Fixed" else size_factor

    final_strategy = {
        "action": signal,
        "position_size": round(100 * dynamic_adjustment, 2),  # percentage of capital
        "frequency": user_settings.get("trade_frequency", "Weekly")
    }

    return final_strategy
