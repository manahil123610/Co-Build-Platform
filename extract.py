"""Extract a clean teammate profile from a pasted post."""

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from google import genai

from config import MAX_EXTRACTION_ATTEMPTS, MODEL_NAME

FIELDS = {"project", "offers", "needs", "hours_per_week", "timezone", "level"}
LEVELS = {"beginner", "intermediate", "advanced"}


class ProfileValidationError(ValueError):
    """The model response does not match the profile schema."""


def validate_profile(value: Any) -> dict[str, Any]:
    """Validate and normalize the model's JSON response."""
    if not isinstance(value, dict):
        raise ProfileValidationError("Expected a JSON object")
    if set(value) != FIELDS:
        missing = sorted(FIELDS - set(value))
        extra = sorted(set(value) - FIELDS)
        raise ProfileValidationError(f"Fields must match the schema; missing={missing}, extra={extra}")

    if not isinstance(value["project"], str):
        raise ProfileValidationError("project must be a string")
    for field in ("offers", "needs"):
        if not isinstance(value[field], list) or any(not isinstance(item, str) for item in value[field]):
            raise ProfileValidationError(f"{field} must be a list of strings")
    hours = value["hours_per_week"]
    if hours is not None and (not isinstance(hours, int) or isinstance(hours, bool) or hours < 0):
        raise ProfileValidationError("hours_per_week must be a non-negative integer or null")
    for field in ("timezone", "level"):
        if value[field] is not None and not isinstance(value[field], str):
            raise ProfileValidationError(f"{field} must be a string or null")
    level = value["level"]
    if level is not None and level not in LEVELS:
        raise ProfileValidationError("level must be beginner, intermediate, advanced, or null")

    return {
        "project": value["project"].strip(),
        "offers": [item.strip() for item in value["offers"] if item.strip()],
        "needs": [item.strip() for item in value["needs"] if item.strip()],
        "hours_per_week": hours,
        "timezone": value["timezone"].strip() if value["timezone"] else None,
        "level": level,
    }


def _clean_post(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email removed]", text)
    text = re.sub(r"(?<!\w)@[A-Za-z0-9_]{1,30}", "[handle removed]", text)
    return re.sub(r"https?://\S+|www\.\S+", "[URL removed]", text)


def _parse_response(response: str) -> dict[str, Any]:
    content = response.strip()
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE)
    return validate_profile(json.loads(content))


def extract_profile(text: str) -> dict[str, Any]:
    """Ask Gemma for a profile, retrying malformed output with its parse error."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=api_key)
    safe_text = _clean_post(text)
    retry_note = ""
    try:
        for attempt in range(MAX_EXTRACTION_ATTEMPTS):
            prompt = (
                "Extract a teammate profile from the post below. Return ONLY a JSON object with exactly these fields: "
                'project (string), offers (array of skill strings), needs (array of skill strings), '
                'hours_per_week (integer or null), timezone (string or null), level '
                '(beginner, intermediate, advanced, or null). Do not infer personal contact details. '
                f"\n{retry_note}\nPost:\n{safe_text}"
            )
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            try:
                return _parse_response(response.text or "")
            except (json.JSONDecodeError, ProfileValidationError) as error:
                retry_note = f"Your previous response failed validation: {error}. Return corrected JSON only."
                if attempt == MAX_EXTRACTION_ATTEMPTS - 1:
                    raise ProfileValidationError(f"Could not extract a valid profile after {MAX_EXTRACTION_ATTEMPTS} attempts: {error}") from error
    finally:
        client.close()
    raise ProfileValidationError("Could not extract a valid profile")
