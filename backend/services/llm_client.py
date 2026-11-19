import os
from dotenv import load_dotenv
from google import genai

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