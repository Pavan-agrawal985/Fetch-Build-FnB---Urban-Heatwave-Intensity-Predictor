import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, make_scorer

print("Delhi Heat Intensity Model Training")

BASE_DIR = Path(__file__).resolve().parent

# Load Dataset
df = pd.read_csv(BASE_DIR / "india_weather_data.csv")

# Filter Delhi Only (Delhi Coordinates)
df = df[(df["latitude"] == 28.6139) & (df["longitude"] == 77.2090)]

print("Delhi Dataset Size:", df.shape)
if df.empty:
    raise ValueError("No Delhi rows found in dataset. Check latitude/longitude filtering.")

# Handle Missing Values
df = df.fillna(df.mean(numeric_only=True))

# Ensure Binary Target
df["heatwave"] = df["heatwave"].astype(int)

# Basic physical-range cleanup to reduce noisy/outlier-driven behavior.
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
print("Delhi Dataset Size (after cleaning):", df.shape)

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

# Hold-out test set (20%) — kept unseen until the very end
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ============================================================
# k-Fold Cross-Validation Setup
# ============================================================

K = 5
skf = StratifiedKFold(n_splits=K, shuffle=True, random_state=42)

scoring = {
    "accuracy": "accuracy",
    "f1": make_scorer(f1_score, zero_division=0),
}

def report_cv(name: str, cv_results: dict) -> None:
    """Pretty-print per-fold and mean scores from cross_validate results."""
    print(f"\n{'=' * 50}")
    print(f"  {name} -- {K}-Fold Cross-Validation Results")
    print(f"{'=' * 50}")
    for metric in ("accuracy", "f1"):
        scores = cv_results[f"test_{metric}"]
        print(f"\n  {metric.upper()} per fold: ", end="")
        print("  ".join(f"Fold {i+1}: {s:.4f}" for i, s in enumerate(scores)))
        print(f"  Mean {metric.upper()}: {scores.mean():.4f}  (±{scores.std():.4f})")

# ----------------------------
# Logistic Regression (Baseline) — with scaling inside a Pipeline
# ----------------------------

lr_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("lr", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
])

print("\nRunning Logistic Regression k-Fold CV ...")
lr_cv = cross_validate(lr_pipeline, X_train_full, y_train_full,
                       cv=skf, scoring=scoring, return_train_score=False)
report_cv("Logistic Regression", lr_cv)

# ----------------------------
# Random Forest (Main Model)
# ----------------------------

rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    class_weight="balanced",
    random_state=42,
)

print("\nRunning Random Forest k-Fold CV ...")
rf_cv = cross_validate(rf_model, X_train_full, y_train_full,
                       cv=skf, scoring=scoring, return_train_score=False)
report_cv("Random Forest", rf_cv)

# ============================================================
# Compare models and pick the best by mean CV F1
# ============================================================

lr_mean_f1 = lr_cv["test_f1"].mean()
rf_mean_f1 = rf_cv["test_f1"].mean()

print(f"\n{'=' * 50}")
print("  Model Comparison (Mean CV F1)")
print(f"{'=' * 50}")
print(f"  Logistic Regression : {lr_mean_f1:.4f}")
print(f"  Random Forest       : {rf_mean_f1:.4f}")

best_name = "Random Forest" if rf_mean_f1 >= lr_mean_f1 else "Logistic Regression"
print(f"\n  >> Best model: {best_name}")

# ============================================================
# Retrain the best model on the FULL training set & evaluate on hold-out test set
# ============================================================

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_full)
X_test_scaled = scaler.transform(X_test)

lr_final = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
lr_final.fit(X_train_scaled, y_train_full)

rf_final = RandomForestClassifier(
    n_estimators=300, max_depth=12, class_weight="balanced", random_state=42
)
rf_final.fit(X_train_full, y_train_full)

print(f"\n{'=' * 50}")
print("  Hold-out Test Set Evaluation")
print(f"{'=' * 50}")
print(f"  Logistic Regression -- Accuracy: {accuracy_score(y_test, lr_final.predict(X_test_scaled)):.4f}"
      f"  F1: {f1_score(y_test, lr_final.predict(X_test_scaled), zero_division=0):.4f}")
print(f"  Random Forest       -- Accuracy: {accuracy_score(y_test, rf_final.predict(X_test)):.4f}"
      f"  F1: {f1_score(y_test, rf_final.predict(X_test), zero_division=0):.4f}")

final_model = rf_final if rf_mean_f1 >= lr_mean_f1 else lr_final
print(f"\n  Final Model Selected: {best_name}")

# Save Model & Scaler
joblib.dump(final_model, BASE_DIR / "delhi_heat_model.pkl")
joblib.dump(scaler, BASE_DIR / "scaler.pkl")
print("  Model & scaler saved successfully")

# Feature Importance (Random Forest only)
if isinstance(final_model, RandomForestClassifier):
    print(f"\n{'=' * 50}")
    print("  Feature Importance")
    print(f"{'=' * 50}")
    for name, imp in sorted(zip(features, final_model.feature_importances_),
                            key=lambda x: x[1], reverse=True):
        print(f"  {name:30s} {imp:.4f}")