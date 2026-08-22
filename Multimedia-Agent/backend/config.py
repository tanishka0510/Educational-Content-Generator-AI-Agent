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


class GeminiLLMWrapper:
    """
    Custom wrapper to mimic LangChain's LLM interface using the google-genai SDK directly.
    Bypasses the need for langchain-google-genai installation.
    """
    def __init__(self, api_key: str):
        from google import genai
        self.client = genai.Client(api_key=api_key)

    def invoke(self, prompt, *args, **kwargs):
        if isinstance(prompt, list):
            text_parts = []
            for msg in prompt:
                # Extract content from LangChain message if possible
                content = getattr(msg, "content", str(msg))
                text_parts.append(content)
            prompt_str = "\n".join(text_parts)
        else:
            prompt_str = str(prompt)

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_str
        )

        class InvokeResult:
            def __init__(self, text):
                self.content = text
                
        return InvokeResult(response.text.strip() if response.text else "")

    def bind_tools(self, tools, *args, **kwargs):
        # Return self as a simple fallback
        return self


def get_llm():
    """
    Returns a configured LLM instance (ChatGroq or fallback GeminiLLMWrapper).
    """
    if Settings.GROQ_API_KEY:
        return ChatGroq(
            api_key=Settings.GROQ_API_KEY,
            model=Settings.MODEL_NAME,
            temperature=Settings.TEMPERATURE,
            max_tokens=Settings.MAX_TOKENS,
        )

    # Fallback to Gemini wrapper
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError(
            "Neither GROQ_API_KEY nor GEMINI_API_KEY is defined in the environment."
        )

    print("GROQ_API_KEY not found. Using Gemini LLM wrapper fallback for Multimedia Agent.")
    return GeminiLLMWrapper(api_key=gemini_key)