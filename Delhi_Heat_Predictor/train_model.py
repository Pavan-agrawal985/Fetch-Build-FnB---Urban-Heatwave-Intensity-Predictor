import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("Delhi Heat Intensity Model Training")

# Load Dataset
df = pd.read_csv("india_weather_data.csv")

# Filter Delhi Only (Delhi Coordinates)
df = df[(df["latitude"] == 28.6139) & (df["longitude"] == 77.2090)]

print("Delhi Dataset Size:", df.shape)

# Handle Missing Values
df = df.fillna(df.mean(numeric_only=True))

# Ensure Binary Target
df["heatwave"] = df["heatwave"].astype(int)

# Features
features = [
    "max_temperature",
    "min_temperature",
    "dew_point",
    "wind_speed",
    "cloud_cover",
    "pressure_surface_level",
    "solar_radiation",
    "max_humidity",
    "min_humidity"
]

X = df[features]
y = df["heatwave"]

# Train Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scaling for Logistic Regression
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ----------------------------
# Logistic Regression (Baseline)
# ----------------------------

print("\nTraining Logistic Regression")

lr = LogisticRegression(max_iter=1000)
lr.fit(X_train_scaled, y_train)

lr_pred = lr.predict(X_test_scaled)
lr_acc = accuracy_score(y_test, lr_pred)

print("Logistic Regression Accuracy:", lr_acc)

# ----------------------------
# Random Forest (Main Model)
# ----------------------------

print("\nTraining Random Forest")

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42
)

rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)

print("Random Forest Accuracy:", rf_acc)

# ----------------------------
# Final Model (Random Forest)
# ----------------------------

final_model = rf

print("\nFinal Model Selected: Random Forest")

# Save Model
joblib.dump(final_model, "delhi_heat_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("\nModel Saved Successfully")

# Feature Importance
print("\nFeature Importance:")

importance = rf.feature_importances_

for i, v in enumerate(importance):
    print(features[i], ":", round(v,3))