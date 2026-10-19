"""List Gemini models whose names contain "gemma"."""

from dotenv import load_dotenv
from google import genai
import os


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing from the environment or .env")

    client = genai.Client(api_key=api_key)
    try:
        models = client.models.list()
        matches = [model.name for model in models if "gemma" in (model.name or "").lower()]
    finally:
        client.close()

    if not matches:
        print("No models containing 'gemma' are available to this API key.")
        return

    for name in matches:
        print(name)


if __name__ == "__main__":
    main()
