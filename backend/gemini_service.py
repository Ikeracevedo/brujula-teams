import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)


def ask_gemini(question: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
    )

    return response.text