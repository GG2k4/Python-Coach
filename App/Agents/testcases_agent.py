import ast
from dotenv import load_dotenv  # type: ignore
import os
import requests # type: ignore
import google.generativeai as genai # type: ignore
import re
from App.Commons.gemini_communication import GeminiCommunication

class TestcaseAgent:
    def __init__(self):
        self.geminiCommunication = GeminiCommunication()

    @staticmethod
    def clean_code_block(response: str) -> str:
        if response.startswith("```") and response.endswith("```"):
            response = response.strip("`")
            response = response.split("python", 1)[-1].strip()
        match = re.search(r'\[(.*)\]', response, re.DOTALL)
        return match.group(1)

    def get_testcases(self, question: str) -> list:
        prompt = f"""Write 5 test cases for the following question in valid Python list-of-dictionaries format:
                    [{{'input': [...], 'expected': '...'}}, ...]
                    Question: {question}
                    Example:
                    Question: Reverse a string.
                    Gemini: [{{'input': ['hello'], 'expected': 'olleh'}}, {{'input': ['world'], 'expected': 'dlrow'}}]
                    There should be no comments, only the testcases."""
        response = self.geminiCommunication.send_prompt_to_gemini(prompt)
        try:
            cleaned_response = self.clean_code_block(response)
            cleaned_response = "[" + cleaned_response + "]"
            test_cases = ast.literal_eval(cleaned_response)
            if isinstance(test_cases, list) == False:
                raise TypeError
            return test_cases
        except Exception as e:
            print(f"Failed to parse response: {response}. Error: {e}")
            return []