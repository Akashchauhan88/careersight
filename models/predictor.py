"""
ML Predictor
────────────
Loads the trained Random Forest model and produces top-N role predictions
from a user's skill vector.
"""

import os
import sys
import numpy as np
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MODEL_FILE, ENCODER_FILE, MODELS_DIR, TOP_N_ROLES
from engine.data_loader import get_role_by_id


def _load_artifacts():
    """Load model, encoder, and skill_id order from disk."""
    model      = joblib.load(MODEL_FILE)
    le         = joblib.load(ENCODER_FILE)
    skill_ids  = joblib.load(os.path.join(MODELS_DIR, "skill_ids.pkl"))
    return model, le, skill_ids


def model_is_trained() -> bool:
    """Return True if all saved model artifacts exist."""
    return all(
        os.path.exists(p) for p in [
            MODEL_FILE,
            ENCODER_FILE,
            os.path.join(MODELS_DIR, "skill_ids.pkl"),
        ]
    )


def predict_top_roles(user_skills: dict[str, float], top_n: int = TOP_N_ROLES) -> list[dict]:
    """
    Predict the top-N most suitable roles for a user's skill profile.

    Parameters
    ----------
    user_skills : {skill_id: level}  where level ∈ [0, 1]
    top_n       : number of predictions to return

    Returns
    -------
    list of dicts sorted by probability descending:
        {rank, role_id, title, category, probability, role_data}
    """
    model, le, skill_ids = _load_artifacts()

    # Build feature vector in the exact same column order as training
    feature_vector = np.array(
        [user_skills.get(sid, 0.0) for sid in skill_ids]
    ).reshape(1, -1)

    # Get probability distribution over all roles
    proba = model.predict_proba(feature_vector)[0]

    # Top-N indices by probability
    top_indices = np.argsort(proba)[::-1][:top_n]

    predictions = []
    for rank, idx in enumerate(top_indices, start=1):
        role_id     = le.inverse_transform([idx])[0]
        probability = round(float(proba[idx]) * 100, 1)
        role_data   = get_role_by_id(role_id)

        predictions.append({
            "rank"       : rank,
            "role_id"    : role_id,
            "title"      : role_data["title"] if role_data else role_id,
            "category"   : role_data["category"] if role_data else "Unknown",
            "probability": probability,
            "role_data"  : role_data,
        })

    return predictions


def get_feature_importances() -> list[dict]:
    """
    Return global feature importances from the Random Forest model.

    Returns list sorted by importance descending:
        {skill_id, importance}
    """
    model, _, skill_ids = _load_artifacts()
    importances = model.feature_importances_

    result = [
        {"skill_id": sid, "importance": round(float(imp), 4)}
        for sid, imp in zip(skill_ids, importances)
    ]
    result.sort(key=lambda x: x["importance"], reverse=True)
    return result
