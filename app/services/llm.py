import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# VALIDATE API KEY
# ============================================================

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(question, context):

    prompt = f"""
You are an AI document assistant.

Your job is to answer the user's question using ONLY the
information provided in the document context.

IMPORTANT RULES:

1. Do not invent information.

2. Do not add information that is not supported by the context.

3. Carefully distinguish between different types of information.

4. If the user asks for programming languages, return only actual
programming languages explicitly mentioned as programming languages.

5. Do not treat human languages such as English, Tamil, Hindi,
or Japanese as programming languages.

6. Do not treat technical skills, technologies, tools, certifications,
workshops, or domains as programming languages.

7. If the answer cannot be found in the context, say:
"I could not find this information in the uploaded document."

8. Keep the answer concise and directly related to the question.

Document context:
{context}

User question:
{question}

Answer:
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text

        if not answer:

            return (
                "The AI model did not return an answer. "
                "Please try again."
            )

        return answer.strip()


    except Exception as e:

        print(
            "Gemini API error:",
            str(e)
        )

        return (
            "There was a problem communicating with "
            "the AI model. Please try again."
        )