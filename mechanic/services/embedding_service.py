import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Safely load local .env during local development; Railway injects variables directly into system env
load_dotenv()

EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")


def get_genai_client():
    """Dynamically retrieve client at runtime to prevent top-level import crashes."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables or Railway configuration!")
    return genai.Client(api_key=api_key)


def generate_document_embedding(text, title=""):
    client = get_genai_client()
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
    client = get_genai_client()
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