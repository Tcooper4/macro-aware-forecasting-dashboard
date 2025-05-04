import numpy as np

def apply_strategy_settings(forecast_df, strategy_settings):
    """
    Adjusts trading strategy based on user-defined settings and detected signals.
    """
    final_signal = forecast_df["Final Signal"].iloc[-1]
    regime = strategy_settings.get("regime", "Neutral")
    risk_level = strategy_settings.get("risk_level", "Medium")
    frequency_preference = strategy_settings.get("frequency", "Weekly")

    # --- Position sizing logic ---
    risk_multiplier = {"Low": 0.5, "Medium": 1.0, "High": 1.5}.get(risk_level, 1.0)
    regime_adjustment = {"Bull": 1.2, "Neutral": 1.0, "Bear": 0.5}.get(regime, 1.0)
    base_size = 10  # Base percentage
    position_size = base_size * risk_multiplier * regime_adjustment
    position_size = min(max(position_size, 1), 100)

    # --- Trade frequency logic ---
    frequency_map = {
        "Daily": "Once per day",
        "Weekly": "Once per week",
        "Monthly": "Once per month"
    }
    frequency = frequency_map.get(frequency_preference, "Once per week")

    # --- Final trade decision ---
    if final_signal == "BUY":
        action = "ENTER LONG POSITION"
    elif final_signal == "SELL":
        action = "ENTER SHORT POSITION"
    else:
        action = "HOLD CASH"

    return {
        "action": action,
        "position_size": round(position_size, 1),
        "frequency": frequency
    }
