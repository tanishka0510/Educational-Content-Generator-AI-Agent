"""
Application configuration for the Multimedia Agent.

Loads environment variables and initializes the LLM.
"""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()


class Settings:
    """
    Global application settings.
    """

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MODEL_NAME = "llama-3.3-70b-versatile"

    TEMPERATURE = 0.2

    MAX_TOKENS = 1024


def get_llm() -> ChatGroq:
    """
    Returns a configured ChatGroq LLM instance.
    """

    if not Settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY not found in .env"
        )

    return ChatGroq(
        api_key=Settings.GROQ_API_KEY,
        model=Settings.MODEL_NAME,
        temperature=Settings.TEMPERATURE,
        max_tokens=Settings.MAX_TOKENS,
    )