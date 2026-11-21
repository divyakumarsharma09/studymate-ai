import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
DIMENSIONS = 768
BATCH_SIZE = 50


def normalize(vector: list) -> list:
    length = sum(x * x for x in vector) ** 0.5
    if length == 0:
        return vector
    return [x / length for x in vector]


def embed_texts(texts: list, task_type: str = "RETRIEVAL_DOCUMENT") -> list:
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=DIMENSIONS,
            ),
        )
        vectors.extend([normalize(item.values) for item in result.embeddings])
    return vectors


def embed_question(question: str) -> list:
    return embed_texts([question], task_type="RETRIEVAL_QUERY")[0]