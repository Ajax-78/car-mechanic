import os
from pathlib import Path
from google.genai import types
from dotenv import load_dotenv
from google import genai



# backend/.env
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


API_KEY = os.getenv("GEMINI_API_KEY")

print("Embedding service API key loaded:", bool(API_KEY))

if not API_KEY:
    raise ValueError(
        f"GEMINI_API_KEY not found. Expected .env at: {BASE_DIR / '.env'}"
    )


client = genai.Client(
    api_key=API_KEY
)


EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)


def generate_document_embedding(text, title=""):

    content = f"title: {title} | text: {text}"

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=content,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        ),
    )

    return result.embeddings[0].values


def generate_query_embedding(text):

    content = f"task: question answering | query: {text}"

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=content,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768,
        ),
    )

    return result.embeddings[0].values
