import numpy as np
import pandas as pd
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "delhi_heat_model.pkl")
scaler = joblib.load(BASE_DIR / "scaler.pkl")

df = pd.read_csv(BASE_DIR / "india_weather_data.csv")
df = df[(df["latitude"] == 28.6139) & (df["longitude"] == 77.2090)]
df = df.fillna(df.mean(numeric_only=True))
df["heatwave"] = df["heatwave"].astype(int)
df = df[
    (df["max_temperature"].between(-10, 60)) &
    (df["min_temperature"].between(-20, 50)) &
    (df["dew_point"].between(-20, 50)) &
    (df["wind_speed"].between(0, 60)) &
    (df["cloud_cover"].between(0, 100)) &
    (df["pressure_surface_level"].between(850, 1100)) &
    (df["solar_radiation"].between(0, 1400))
].copy()
df["max_humidity"] = df["max_humidity"].clip(lower=0, upper=100)
df["min_humidity"] = df["min_humidity"].clip(lower=0, upper=100)

features = [
    "max_temperature", "min_temperature", "dew_point",
    "wind_speed", "cloud_cover", "pressure_surface_level",
    "solar_radiation", "max_humidity", "min_humidity"
]

np.random.seed(42)
sample = df.sample(n=min(20, len(df)), random_state=42)
X_sample = sample[features]

proba = model.predict_proba(X_sample)[:, 1]
intensity = proba * 100.0

def categorize(score):
    if score < 40:
        return "Low"
    elif score < 70:
        return "Medium"
    else:
        return "High"

results = pd.DataFrame({
    "Temp (°C)": sample["max_temperature"].values,
    "Humidity (%)": sample["max_humidity"].values,
    "Intensity": np.round(intensity, 1),
    "Category": [categorize(s) for s in intensity]
})

results = results.sort_values("Intensity").reset_index(drop=True)

header = f"{'Temp (°C)':>12}  {'Humidity (%)':>14}  {'Intensity':>11}  {'Category'}"
sep = "-" * len(header)
print(f"\n  Delhi Urban Heatwave Intensity — Test Predictions")
print(f"  {sep}")
print(f"  {header}")
print(f"  {sep}")
for _, row in results.iterrows():
    print(f"  {row['Temp (°C)']:>12.1f}  {row['Humidity (%)']:>14.1f}  {row['Intensity']:>11.1f}  {row['Category']}")
print(f"  {sep}")

counts = results["Category"].value_counts()
print(f"\n  Summary: {counts.get('Low', 0)} Low | {counts.get('Medium', 0)} Medium | {counts.get('High', 0)} High  (out of {len(results)} samples)")
