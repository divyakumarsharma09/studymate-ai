import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL")


def ask_llm(history: list) -> str:
    contents = [
        {"role": m["role"], "parts": [{"text": m["content"]}]}
        for m in history
    ]
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
    )
    return response.text


def ask_llm_json(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )
    return response.text