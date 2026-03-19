"""
SHAP Explainer
──────────────
Uses SHAP TreeExplainer to explain why the Random Forest predicted
a specific role for a given user's skill profile.

SHAP (SHapley Additive exPlanations) assigns each skill a contribution
value — positive means the skill pushed toward this prediction,
negative means it pushed away.

Reference:
    Lundberg & Lee (2017). "A unified approach to interpreting model predictions."
    NeurIPS 2017. https://arxiv.org/abs/1705.07874
"""

import os
import sys
import numpy as np
import shap
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MODEL_FILE, ENCODER_FILE, MODELS_DIR, SHAP_MAX_DISPLAY
from engine.data_loader import get_skill_by_id


def _load_artifacts():
    model     = joblib.load(MODEL_FILE)
    le        = joblib.load(ENCODER_FILE)
    skill_ids = joblib.load(os.path.join(MODELS_DIR, "skill_ids.pkl"))
    return model, le, skill_ids


def explain_prediction(
    user_skills: dict[str, float],
    role_id: str,
    top_n: int = SHAP_MAX_DISPLAY,
) -> dict:
    """
    Compute SHAP values for a single user-role prediction.

    Parameters
    ----------
    user_skills : {skill_id: level}
    role_id     : the role to explain
    top_n       : number of top features to return

    Returns
    -------
    {
        "shap_values"    : list[dict]  top-n features with shap value + skill info,
        "base_value"     : float       expected model output,
        "predicted_class": str         role_id predicted,
        "skill_ids"      : list[str]   full feature order,
    }
    """
    model, le, skill_ids = _load_artifacts()

    # Build feature vector
    X = np.array(
        [user_skills.get(sid, 0.0) for sid in skill_ids]
    ).reshape(1, -1)

    # Get class index for target role
    try:
        class_idx = list(le.classes_).index(role_id)
    except ValueError:
        return {"error": f"role_id {role_id} not in model classes"}

    # Compute SHAP values using TreeExplainer (fast, exact for RF)
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)          # shape: (n_classes, 1, n_features)

    if isinstance(shap_values, list):
        role_shap = shap_values[class_idx][0]       # shape: (n_features,)
    else:
        role_shap = shap_values[0, :, class_idx]

    base_value = (
        explainer.expected_value[class_idx]
        if isinstance(explainer.expected_value, (list, np.ndarray))
        else explainer.expected_value
    )

    # Build enriched result list
    feature_contribs = []
    for sid, sv, user_val in zip(skill_ids, role_shap, X[0]):
        skill_info = get_skill_by_id(sid) or {}
        feature_contribs.append({
            "skill_id"   : sid,
            "skill_name" : skill_info.get("skill_name", sid),
            "category"   : skill_info.get("category", "Unknown"),
            "shap_value" : float(sv),
            "user_level" : float(user_val),
            "direction"  : "positive" if sv >= 0 else "negative",
        })

    # Sort by absolute SHAP value — most influential first
    feature_contribs.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    return {
        "shap_features" : feature_contribs[:top_n],
        "all_features"  : feature_contribs,
        "base_value"    : float(base_value),
        "role_id"       : role_id,
        "skill_ids"     : skill_ids,
    }
