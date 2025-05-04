import wbdata
import pandas as pd

# Get all indicators from World Bank
indicators = wbdata.get_indicators()

# Convert list of dicts to DataFrame
indicators_df = pd.DataFrame(indicators)

# Optional: filter for CO₂ or emissions-related indicators
co2_df = indicators_df[indicators_df["name"].str.contains("CO2|emissions|carbon", case=False, na=False)]

# Save to CSV
co2_df.to_csv("co2_indicators.csv", index=False)

# Print preview
print(co2_df[["id", "name"]].head(20))
