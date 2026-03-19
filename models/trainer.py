"""
ML Model Trainer
────────────────
Trains a Random Forest classifier to predict the most suitable career role
from a user's skill profile vector.

Run this script once from the project root:
    python models/trainer.py

The trained model and label encoder are saved to models/saved/.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report

from engine.data_loader import build_feature_matrix, load_roles
from config import (
    RF_N_ESTIMATORS, RF_MAX_DEPTH, RF_RANDOM_STATE,
    MODEL_FILE, ENCODER_FILE, MODELS_DIR
)


def generate_training_data(
    X_roles: pd.DataFrame,
    skill_ids: list[str],
    samples_per_role: int = 80,
    noise_std: float = 0.15,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Since we have 63 role archetypes but no real user records,
    we generate synthetic training samples by adding Gaussian noise
    to each role's importance vector — simulating real users with
    varying skill levels around each role's ideal profile.

    This is a standard technique in small-data research settings and
    is documented as such in the thesis.
    """
    rng = np.random.default_rng(seed)
    X_list, y_list = [], []

    for role_id, row in X_roles.iterrows():
        base = row.values.astype(float)
        for _ in range(samples_per_role):
            noise  = rng.normal(0, noise_std, size=len(base))
            sample = np.clip(base + noise, 0.0, 1.0)
            X_list.append(sample)
            y_list.append(role_id)

    return np.array(X_list), np.array(y_list)


def train_and_save():
    print("Loading feature matrix …")
    X_roles, skill_ids = build_feature_matrix()

    print(f"Generating synthetic training data ({80} samples × {len(X_roles)} roles) …")
    X_train, y_train = generate_training_data(X_roles, skill_ids)

    print(f"Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features")

    # Encode role_id labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_train)

    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators = RF_N_ESTIMATORS,
        max_depth    = RF_MAX_DEPTH,
        random_state = RF_RANDOM_STATE,
        n_jobs       = -1,
        class_weight = "balanced",
    )

    print("Training Random Forest …")
    model.fit(X_train, y_encoded)

    # Cross-validation
    print("Running 5-fold cross-validation …")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RF_RANDOM_STATE)
    cv_scores = cross_val_score(model, X_train, y_encoded, cv=cv, scoring="accuracy")
    print(f"CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # Save model and encoder
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(le,    ENCODER_FILE)
    # Also save the skill_ids column order so inference is consistent
    joblib.dump(skill_ids, os.path.join(MODELS_DIR, "skill_ids.pkl"))

    print(f"\nModel saved  → {MODEL_FILE}")
    print(f"Encoder saved → {ENCODER_FILE}")
    print("Training complete.")

    return model, le, cv_scores


if __name__ == "__main__":
    train_and_save()
