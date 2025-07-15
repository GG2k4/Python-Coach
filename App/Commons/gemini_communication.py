from dotenv import load_dotenv  # type: ignore
import os
import requests # type: ignore
import google.generativeai as genai # type: ignore

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiCommunication:
    def __init__(self):
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def send_prompt_to_gemini(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"