import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set. Please set it in your environment or a .env file.")

# Setup Gemini once
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

def summarize_with_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()