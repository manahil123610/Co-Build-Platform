"""Create concise fit explanations and user-editable intro drafts."""

from typing import Any


def explain(a: dict[str, Any], b: dict[str, Any], matched: dict[str, Any]) -> str:
    skills = matched.get("matched_skills", [])
    if skills:
        return f"You complement each other on {', '.join(skills)}."
    if a.get("timezone") and a.get("timezone") == b.get("timezone"):
        return "You share a timezone and can compare the skills each of you needs."
    return "Your profiles may complement each other; compare your offers and needs to see if the fit is right."


def draft_intro(a: dict[str, Any], b: dict[str, Any]) -> str:
    project = a.get("project") or "your project"
    their_project = b.get("project") or "your project"
    skills = sorted(set(b.get("offers", [])) & set(a.get("needs", [])))
    detail = f"Your experience with {', '.join(skills)} looks relevant." if skills else "Our profiles seem like they could complement each other."
    return (
        f"Hi! I came across your post about {project}. {detail} "
        f"I'm interested in learning more about {their_project} and seeing whether our skills and availability line up. "
        "Would you be open to a quick chat?"
    )
