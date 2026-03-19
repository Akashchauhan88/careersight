"""
Skill Matching Engine
─────────────────────
Computes a weighted compatibility score between a user's skill profile
and any career role using the O*NET importance scores as weights.

Formula (O*NET-inspired weighted sum):

    compatibility = Σ (user_level_i × importance_i)
                    ─────────────────────────────────  × 100
                         Σ importance_i

Where user_level_i ∈ [0, 1]  and importance_i ∈ [0, 1].

A score of 100 means the user meets every skill at exactly the required
importance level. Scores > 100 are capped at 100.
"""

import pandas as pd
import numpy as np

from engine.data_loader import get_skills_for_role, load_matrix, load_roles
from config import MIN_IMPORTANCE_THRESHOLD


def compute_compatibility(user_skills: dict[str, float], role_id: str) -> dict:
    """
    Compute the compatibility score between a user and a role.

    Parameters
    ----------
    user_skills : {skill_id: user_level}  where user_level ∈ [0, 1]
    role_id     : target role identifier

    Returns
    -------
    {
        "score"         : float  (0–100),
        "strengths"     : list of dicts  (skills where user ≥ importance),
        "gaps"          : list of dicts  (skills where user < importance),
        "skill_details" : list of dicts  (all skills with comparison info),
    }
    """
    role_skills = get_skills_for_role(role_id)
    role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]

    if role_skills.empty:
        return {"score": 0.0, "strengths": [], "gaps": [], "skill_details": []}

    weighted_sum   = 0.0
    importance_sum = 0.0
    strengths      = []
    gaps           = []
    skill_details  = []

    for _, row in role_skills.iterrows():
        sid         = row["skill_id"]
        importance  = row["importance_score"]
        user_level  = user_skills.get(sid, 0.0)
        contribution = user_level * importance

        weighted_sum   += contribution
        importance_sum += importance

        detail = {
            "skill_id"       : sid,
            "skill_name"     : row["skill_name"],
            "category"       : row["category"],
            "importance"     : importance,
            "user_level"     : user_level,
            "gap"            : max(0.0, importance - user_level),
            "level_required" : row["level_required"],
        }
        skill_details.append(detail)

        if user_level >= importance:
            strengths.append(detail)
        else:
            gaps.append(detail)

    score = min(100.0, (weighted_sum / importance_sum) * 100) if importance_sum > 0 else 0.0

    # Sort: strengths by user_level desc, gaps by gap desc (biggest first)
    strengths.sort(key=lambda x: x["user_level"], reverse=True)
    gaps.sort(key=lambda x: x["gap"], reverse=True)

    return {
        "score"        : round(score, 1),
        "strengths"    : strengths,
        "gaps"         : gaps,
        "skill_details": skill_details,
    }


def rank_all_roles(user_skills: dict[str, float]) -> pd.DataFrame:
    """
    Score the user against every role and return a ranked DataFrame.

    Returns
    -------
    DataFrame with columns:
        role_id, title, category, score, demand_level, salary_min, salary_max
    Sorted by score descending.
    """
    roles  = load_roles()
    rows   = []

    for role in roles:
        result = compute_compatibility(user_skills, role["role_id"])
        rows.append({
            "role_id"     : role["role_id"],
            "title"       : role["title"],
            "category"    : role["category"],
            "score"       : result["score"],
            "demand_level": role["demand_level"],
            "salary_min"  : role["salary_range"]["min"],
            "salary_max"  : role["salary_range"]["max"],
            "growth_rate" : role["growth_rate"],
        })

    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    df.index += 1  # 1-based rank
    return df


def get_skill_vectors(role_id: str, user_skills: dict[str, float]) -> tuple[list, list, list]:
    """
    Extract aligned skill vectors for radar chart plotting.

    Returns
    -------
    skill_names   : list[str]
    role_vector   : list[float]  (importance scores)
    user_vector   : list[float]  (user levels, clipped to importance)
    """
    role_skills = get_skills_for_role(role_id)
    role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]

    skill_names = role_skills["skill_name"].tolist()
    role_vector = role_skills["importance_score"].tolist()
    user_vector = [
        min(user_skills.get(sid, 0.0), 1.0)
        for sid in role_skills["skill_id"]
    ]
    return skill_names, role_vector, user_vector
