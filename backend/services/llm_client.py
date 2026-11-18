import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL")
def ask_llm(message:str)->str:
    response=client.models.generate_content(
        model=MODEL,
        contents=message,
    )
    return response.text