import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)

model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

try:
    response = client.models.generate_content(
        model=model_name,
        contents="Reply with exactly: Gemini is working",
    )

    print("Model:", model_name)
    print("Response:", response.text)

except Exception as e:
    print("Gemini test failed:")
    print(type(e).__name__, e)