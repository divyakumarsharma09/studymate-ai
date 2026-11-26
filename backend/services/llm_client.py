import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL")

RETRY_CODES = {500, 503, 504}
MAX_ATTEMPTS = 3


def with_retry(call):
    for attempt in range(MAX_ATTEMPTS):
        try:
            return call()
        except errors.APIError as error:
            code = getattr(error, "code", None)
            if code not in RETRY_CODES or attempt == MAX_ATTEMPTS - 1:
                raise
            print(f"Gemini error {code}, retrying (attempt {attempt + 2} of {MAX_ATTEMPTS})")
            time.sleep(2 * (attempt + 1))


def ask_llm(history: list) -> str:
    contents = [
        {"role": m["role"], "parts": [{"text": m["content"]}]}
        for m in history
    ]
    response = with_retry(
        lambda: client.models.generate_content(model=MODEL, contents=contents)
    )
    return response.text


def ask_llm_json(prompt: str) -> str:
    response = with_retry(
        lambda: client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )
    )
    return response.text


def ask_llm_image(prompt: str, image_bytes: bytes, mime_type: str) -> str:
    response = with_retry(
        lambda: client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
        )
    )
    return response.text