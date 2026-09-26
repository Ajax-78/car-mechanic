import json
import logging
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

load_dotenv()

# Primary model from env with automated fallback chain
PRIMARY_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]

# Deduplicate while preserving order
MODELS_TO_TRY = list(dict.fromkeys(FALLBACK_MODELS))

SYSTEM_INSTRUCTION = """
You are an expert AI automotive mechanic assistant.
Your goal is to diagnose vehicle issues, offer clear troubleshooting steps, 
and provide safety advice. If the problem is dangerous, recommend professional inspection immediately.
"""

def get_genai_client():
    """Retrieve client dynamically at runtime rather than on module import."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables or Railway configuration!")
    return genai.Client(api_key=api_key)

def generate_mechanic_response(
    question,
    context,
    conversation_history="",
    max_retries_per_model=2
):
    client = get_genai_client()

    prompt = f"""
RELEVANT MECHANIC KNOWLEDGE:
--------------------------------
{context}
--------------------------------

PREVIOUS CONVERSATION:
--------------------------------
{conversation_history}
--------------------------------

CURRENT USER QUESTION:
--------------------------------
{question}
--------------------------------
"""

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "diagnosis_ready": {"type": "BOOLEAN"},
                "follow_up_question": {"type": "STRING"},
                "issue": {"type": "STRING"},
                "severity": {"type": "STRING"},
                "possible_causes": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "explanation": {"type": "STRING"},
                "recommendation": {"type": "STRING"},
                "safety_warning": {"type": "STRING"},
                "confidence": {"type": "NUMBER"}
            },
            "required": [
                "diagnosis_ready",
                "follow_up_question",
                "issue",
                "severity",
                "possible_causes",
                "explanation",
                "recommendation",
                "safety_warning",
                "confidence"
            ]
        },
        temperature=0.2
    )

    last_exception = None

    for model_name in MODELS_TO_TRY:
        delay = 1
        for attempt in range(1, max_retries_per_model + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )

                response_text = ""
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
                else:
                    response_text = response.text or ""

                try:
                    return json.loads(response_text)
                except (json.JSONDecodeError, TypeError):
                    return {
                        "diagnosis_ready": False,
                        "follow_up_question": response_text,
                        "issue": "",
                        "severity": "unknown",
                        "possible_causes": [],
                        "explanation": response_text,
                        "recommendation": "",
                        "safety_warning": "",
                        "confidence": 0.0
                    }

            except APIError as e:
                last_exception = e
                if e.code in (503, 429):
                    logger.warning(
                        f"[Gemini API - {model_name}] HTTP {e.code}. Retrying in {delay}s (Attempt {attempt}/{max_retries_per_model})..."
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise e

        logger.warning(f"[Gemini API] Model {model_name} failed all retries. Falling back to next model...")

    if last_exception:
        raise last_exception
    raise RuntimeError("All configured Gemini models are currently unavailable.")