import os
import time
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Retry config
MAX_RETRIES = 3
BASE_DELAY = 1.0      # seconds
MAX_DELAY = 16.0      # seconds cap
REQUEST_TIMEOUT = 30  # seconds


def _build_headers() -> dict:
    if not GROQ_API_KEY:
        raise EnvironmentError("GROQ_API_KEY is not set in environment variables.")
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }


def _call_groq(prompt: str) -> str:
    """
    Call the Groq API with exponential backoff retry logic.
    Handles timeouts, rate limits (429), and server errors (5xx).
    """
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.5,
    }

    last_exception: Optional[Exception] = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                response = client.post(GROQ_API_URL, json=payload, headers=_build_headers())

            # Rate limited — back off and retry
            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", BASE_DELAY * (2 ** attempt)))
                wait = min(retry_after, MAX_DELAY)
                logger.warning(f"Groq rate limited. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                last_exception = Exception(f"Rate limited by Groq API (429)")
                continue

            # Server-side error — retry with backoff
            if response.status_code >= 500:
                wait = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                logger.warning(f"Groq server error {response.status_code}. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                last_exception = Exception(f"Groq server error: {response.status_code}")
                continue

            # Client error (4xx other than 429) — don't retry
            if response.status_code >= 400:
                error_detail = response.json().get("error", {}).get("message", response.text)
                raise ValueError(f"Groq API client error {response.status_code}: {error_detail}")

            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except httpx.TimeoutException as e:
            wait = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
            logger.warning(f"Groq request timed out. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
            last_exception = e

        except httpx.RequestError as e:
            wait = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
            logger.warning(f"Groq network error: {e}. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
            last_exception = e

    raise RuntimeError(
        f"Groq API failed after {MAX_RETRIES} attempts. Last error: {last_exception}"
    )


def generate_summary(note_content: str) -> str:
    """Generate an AI summary for a note's content."""
    prompt = (
        f"Summarize the following note in 2–4 concise sentences. "
        f"Capture the key ideas clearly and directly.\n\nNote:\n{note_content}"
    )
    return _call_groq(prompt)


def generate_tags(note_content: str) -> list[str]:
    """Generate relevant tags for a note's content."""
    prompt = (
        f"Analyze the following note and suggest 3–6 short, relevant tags "
        f"(single words or short phrases). Return ONLY a JSON array of strings, "
        f"e.g. [\"python\", \"machine learning\", \"tutorial\"]. No explanation.\n\n"
        f"Note:\n{note_content}"
    )
    import json
    raw = _call_groq(prompt)
    # Strip any markdown fences just in case
    raw = raw.strip().strip("```json").strip("```").strip()
    try:
        tags = json.loads(raw)
        if isinstance(tags, list):
            return [str(t).strip() for t in tags if t]
    except json.JSONDecodeError:
        logger.warning(f"Could not parse tags JSON from Groq: {raw}")
    # Fallback: split by comma
    return [t.strip().strip('"') for t in raw.strip("[]").split(",") if t.strip()]