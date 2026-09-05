import os
import requests

from dotenv import load_dotenv
from google import genai


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv(override=True)

# Try initializing GenAI client if GEMINI_API_KEY is present
gemini_key = os.getenv("GEMINI_API_KEY")
client = None
if gemini_key:
    try:
        client = genai.Client(api_key=gemini_key)
    except Exception as e:
        print("Could not initialize Gemini Client:", e)


# ============================================================
# Ask Gemini
# ============================================================

def ask_gemini(prompt: str) -> str:
    """
    Query the configured LLM. Prioritizes Groq API if GROQ_API_KEY is defined.
    Falls back to Gemini if GROQ_API_KEY is not available.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print("Using Groq API (groq/compound) for chat generation...")
        
        # Truncate prompt if it is too large to prevent 413 Payload Too Large on Groq Free Tier
        # We keep the first 20,000 chars (context) and last 5,000 chars (rules/instructions)
        safe_prompt = prompt
        if len(prompt) > 25000:
            print(f"Truncating prompt from {len(prompt)} to 25000 characters for Groq safety.")
            safe_prompt = prompt[:20000] + "\n\n[Context truncated due to size limits]\n\n" + prompt[-5000:]

        try:
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "groq/compound",
                "messages": [{"role": "user", "content": safe_prompt}],
                "temperature": 0.2,
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print("Groq API error, falling back to Gemini:", e)
            if not client:
                raise e

    # Fallback to Gemini
    if not client:
        raise ValueError("Neither GROQ_API_KEY nor GEMINI_API_KEY is available in the environment.")
    
    last_err = None
    for model_name in ["gemini-3.6-flash", "gemini-2.5-flash-lite", "gemini-3.5-flash"]:
        try:
            print(f"Calling Gemini fallback model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as gemini_err:
            print(f"Gemini model {model_name} failed: {gemini_err}. Trying next model...")
            last_err = gemini_err
            
    raise last_err