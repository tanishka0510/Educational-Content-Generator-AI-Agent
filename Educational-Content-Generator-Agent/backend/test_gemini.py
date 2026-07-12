from services.gemini_service import ask_gemini

response = ask_gemini(
    "Explain Artificial Intelligence in one sentence."
)

print(response)