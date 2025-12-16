# app/services/gemini_client.py
import json
import requests

from app.core.config import settings

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-1.5-flash:generateContent"
)


def ask_gemini(prompt: str) -> str:
    """
    Call Gemini with a simple text prompt and return the generated text.
    Raises RuntimeError if anything goes wrong.
    """
    params = {"key": settings.GEMINI_API_KEY}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    resp = requests.post(GEMINI_ENDPOINT, params=params, json=body, timeout=40)

    if not resp.ok:
        raise RuntimeError(f"Gemini error {resp.status_code}: {resp.text}")

    data = resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        # In case Google changes the schema a bit
        raise RuntimeError(
            "Unexpected Gemini response: " + json.dumps(data)[:500]
        )
