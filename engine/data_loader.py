"""
Data loading layer.
All three data files are loaded once and cached by Streamlit's
@st.cache_data so they are never re-read on rerun.
"""

import json
import pandas as pd
import streamlit as st

from config import ROLES_FILE, SKILLS_FILE, MATRIX_FILE


# ── Raw loaders (cached) ────────────────────────────────────────────────────

@st.cache_data
def load_roles() -> list[dict]:
    """Return list of role dicts from roles_master.json."""
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["roles"]


@st.cache_data
def load_skills() -> list[dict]:
    """Return list of skill dicts from skill_taxonomy.json."""
    with open(SKILLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["skills"]


@st.cache_data
def load_matrix() -> pd.DataFrame:
    """Return the role-skill matrix as a DataFrame."""
    return pd.read_csv(MATRIX_FILE)


# ── Derived helpers (also cached) ──────────────────────────────────────────

@st.cache_data
def get_role_by_id(role_id: str) -> dict | None:
    """Look up a single role dict by its role_id."""
    return next((r for r in load_roles() if r["role_id"] == role_id), None)


@st.cache_data
def get_skill_by_id(skill_id: str) -> dict | None:
    """Look up a single skill dict by its skill_id."""
    return next((s for s in load_skills() if s["skill_id"] == skill_id), None)


@st.cache_data
def get_skills_for_role(role_id: str) -> pd.DataFrame:
    """
    Return a DataFrame of skills required for a role, enriched with
    skill names and categories from the taxonomy.

    Columns: skill_id, skill_name, category, importance_score, level_required
    """
    matrix = load_matrix()
    skills = load_skills()

    skill_lookup = {s["skill_id"]: s for s in skills}
    role_skills  = matrix[matrix["role_id"] == role_id].copy()

    role_skills["skill_name"] = role_skills["skill_id"].map(
        lambda sid: skill_lookup.get(sid, {}).get("skill_name", sid)
    )
    role_skills["category"] = role_skills["skill_id"].map(
        lambda sid: skill_lookup.get(sid, {}).get("category", "Unknown")
    )

    return role_skills.sort_values("importance_score", ascending=False).reset_index(drop=True)


@st.cache_data
def get_all_role_titles() -> dict[str, str]:
    """Return {role_id: title} for all roles — used in dropdowns."""
    return {r["role_id"]: r["title"] for r in load_roles()}


@st.cache_data
def get_roles_by_category() -> dict[str, list[dict]]:
    """Return roles grouped by category."""
    from collections import defaultdict
    grouped = defaultdict(list)
    for role in load_roles():
        grouped[role["category"]].append(role)
    return dict(grouped)


@st.cache_data
def build_feature_matrix() -> tuple[pd.DataFrame, list[str]]:
    """
    Build the ML feature matrix (roles × skills) where each cell is
    the importance_score (0 if the skill is not required for that role).

    Returns
    -------
    X : DataFrame  shape (n_roles, n_skills)
    skill_ids : list of skill_id strings (column order)
    """
    matrix = load_matrix()
    pivot  = matrix.pivot_table(
        index="role_id",
        columns="skill_id",
        values="importance_score",
        fill_value=0.0,
    )
    return pivot, list(pivot.columns)
