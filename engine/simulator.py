"""
What-If Simulation Engine
─────────────────────────
Allows users to hypothetically boost their skills and see how
their compatibility score changes — before and after.
"""

import copy
from engine.skill_matcher import compute_compatibility


def simulate_improvement(
    base_skills: dict[str, float],
    improvements: dict[str, float],
    role_id: str,
) -> dict:
    """
    Compute before / after compatibility when a user improves specific skills.

    Parameters
    ----------
    base_skills   : current skill profile  {skill_id: level}
    improvements  : proposed skill deltas  {skill_id: delta}  e.g. {"S001": 0.3}
    role_id       : target role

    Returns
    -------
    {
        "before"       : result dict from compute_compatibility,
        "after"        : result dict from compute_compatibility,
        "score_delta"  : float  (after.score - before.score),
        "improved_skills": list of {skill_id, from, to},
    }
    """
    before = compute_compatibility(base_skills, role_id)

    improved_skills_log = []
    updated = copy.deepcopy(base_skills)

    for skill_id, delta in improvements.items():
        old_val = updated.get(skill_id, 0.0)
        new_val = min(1.0, old_val + delta)
        updated[skill_id] = new_val
        improved_skills_log.append({
            "skill_id": skill_id,
            "from"    : round(old_val, 2),
            "to"      : round(new_val, 2),
            "delta"   : round(new_val - old_val, 2),
        })

    after = compute_compatibility(updated, role_id)

    return {
        "before"          : before,
        "after"           : after,
        "score_delta"     : round(after["score"] - before["score"], 1),
        "improved_skills" : improved_skills_log,
        "updated_skills"  : updated,
    }


def recommend_top_improvements(
    user_skills: dict[str, float],
    role_id: str,
    top_n: int = 5,
) -> list[dict]:
    """
    Identify the top-n skills that would most improve the compatibility score
    if the user raised them by 0.3 (one level step).

    Returns list of dicts sorted by score impact descending:
        {skill_id, skill_name, current_level, importance, score_gain}
    """
    result   = compute_compatibility(user_skills, role_id)
    gains    = []

    for gap_skill in result["gaps"]:
        sid     = gap_skill["skill_id"]
        current = gap_skill["user_level"]
        imp     = gap_skill["importance"]

        # Simulate +0.3 on this single skill
        sim = simulate_improvement(user_skills, {sid: 0.3}, role_id)
        gain = sim["score_delta"]

        gains.append({
            "skill_id"     : sid,
            "skill_name"   : gap_skill["skill_name"],
            "category"     : gap_skill["category"],
            "current_level": current,
            "importance"   : imp,
            "score_gain"   : gain,
            "level_required": gap_skill["level_required"],
        })

    gains.sort(key=lambda x: x["score_gain"], reverse=True)
    return gains[:top_n]
