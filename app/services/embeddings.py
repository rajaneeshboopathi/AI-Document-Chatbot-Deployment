import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# EMBEDDING CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "gemini-embedding-2"

EMBEDDING_DIMENSION = 768


# ============================================================
# GENERATE EMBEDDING
# ============================================================

def generate_embedding(text):

    """
    Generate a semantic embedding using
    Gemini's embedding model.

    Returns:
        list[float]: 768-dimensional embedding
    """

    result = client.models.embed_content(

        model=EMBEDDING_MODEL,

        contents=text,

        config={
            "output_dimensionality": EMBEDDING_DIMENSION
        }
    )

    return result.embeddings[0].values