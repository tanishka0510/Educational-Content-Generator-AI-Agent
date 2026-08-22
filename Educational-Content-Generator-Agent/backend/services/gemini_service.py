import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# Create Gemini Client
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# Ask Gemini
# ============================================================

def ask_gemini(prompt: str):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text