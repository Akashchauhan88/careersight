"""General-purpose helper functions used throughout the app."""

from config import BAND_EXCELLENT, BAND_GOOD, BAND_MODERATE


def score_to_band(score: float) -> tuple[str, str]:
    """
    Convert a 0-100 compatibility score to a (label, colour) tuple.

    Returns
    -------
    (band_label, hex_colour)
    """
    if score >= BAND_EXCELLENT:
        return "Excellent Match", "#1D9E75"
    elif score >= BAND_GOOD:
        return "Good Match", "#BA7517"
    elif score >= BAND_MODERATE:
        return "Developing", "#185FA5"
    else:
        return "Early Stage", "#E24B4A"


def format_salary(salary_range: dict) -> str:
    """Format salary dict → readable string e.g. '$95,000 – $165,000 USD'."""
    lo  = salary_range.get("min", 0)
    hi  = salary_range.get("max", 0)
    cur = salary_range.get("currency", "USD")
    return f"${lo:,.0f} – ${hi:,.0f} {cur}"


def format_growth(rate: float) -> str:
    """Format growth rate → '↑ 36 % projected growth'."""
    arrow = "↑" if rate > 0 else "↓"
    return f"{arrow} {abs(rate):.0f}% projected growth"


def skill_level_from_score(score: float) -> str:
    """Map an importance score to a human-readable level."""
    if score >= 0.8:
        return "Advanced"
    elif score >= 0.6:
        return "Intermediate"
    return "Beginner"


def gap_description(user_score: float, required_score: float) -> str:
    """Describe the gap between user skill and role requirement."""
    gap = required_score - user_score
    if gap <= 0:
        return "✅ Meets requirement"
    elif gap <= 0.25:
        return "🟡 Small gap"
    elif gap <= 0.5:
        return "🟠 Moderate gap"
    else:
        return "🔴 Significant gap"


def truncate(text: str, max_chars: int = 120) -> str:
    """Truncate long strings for compact display."""
    return text if len(text) <= max_chars else text[:max_chars].rstrip() + "…"
