"""Complementary-skill profile matching."""

import json
import re
from pathlib import Path
from typing import Any

from config import HOURS_BONUS, MATCH_LIMIT, TIMEZONE_BONUS

SYNONYMS = {
    "react": "frontend", "react.js": "frontend", "frontend": "frontend", "web ui": "frontend",
    "user interface": "frontend", "ui": "frontend",
    "node": "backend", "node.js": "backend", "api": "backend", "backend": "backend",
    "server-side": "backend", "python": "python", "machine learning": "ml", "ml": "ml",
    "ai": "ml", "artificial intelligence": "ml", "ux": "design", "ui design": "design",
    "visual design": "design", "design": "design", "figma": "design",
    "copywriting": "writing", "content writing": "writing", "writer": "writing", "writing": "writing",
    "ios": "mobile", "android": "mobile", "mobile development": "mobile", "mobile": "mobile",
}


def normalize_skill(skill: str) -> str:
    """Map common alternate skill names to one comparable term."""
    normalized = re.sub(r"\s+", " ", skill.strip().lower())
    return SYNONYMS.get(normalized, normalized)


def _coverage(needed: list[str], offered: list[str]) -> tuple[float, list[str]]:
    offered_set = {normalize_skill(skill) for skill in offered}
    matched = sorted({normalize_skill(skill) for skill in needed} & offered_set)
    return (len(matched) / len(needed) if needed else 0.0), matched


def score(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Return normalized reciprocal coverage, small coordination bonuses, and matches."""
    a_covered, a_matched = _coverage(a.get("needs", []), b.get("offers", []))
    b_covered, b_matched = _coverage(b.get("needs", []), a.get("offers", []))
    total_needs = len(a.get("needs", [])) + len(b.get("needs", []))
    base = (a_covered * len(a.get("needs", [])) + b_covered * len(b.get("needs", []))) / total_needs if total_needs else 0.0
    bonuses = 0.0
    hours_a, hours_b = a.get("hours_per_week"), b.get("hours_per_week")
    if hours_a is not None and hours_b is not None and min(hours_a, hours_b) > 0:
        bonuses += HOURS_BONUS * min(hours_a, hours_b) / max(hours_a, hours_b)
    timezone_a, timezone_b = a.get("timezone"), b.get("timezone")
    if timezone_a and timezone_b and timezone_a.casefold() == timezone_b.casefold():
        bonuses += TIMEZONE_BONUS
    return {
        "score": round(min(1.0, base + bonuses), 4),
        "matched_skills": sorted(set(a_matched + b_matched)),
        "a_needs_covered": a_matched,
        "b_needs_covered": b_matched,
    }


def load_profiles(path: str | Path = "data/profiles.json") -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as file:
        data = json.load(file)
    return data["profiles"]


def top_matches(profile: dict[str, Any], profiles: list[dict[str, Any]], limit: int = MATCH_LIMIT) -> list[dict[str, Any]]:
    results = []
    for candidate in profiles:
        if candidate.get("id") == profile.get("id"):
            continue
        results.append({"profile": candidate, **score(profile, candidate)})
    return sorted(results, key=lambda item: item["score"], reverse=True)[:limit]
