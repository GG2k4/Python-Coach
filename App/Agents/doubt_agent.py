from dotenv import load_dotenv  # type: ignore
import os
import requests # type: ignore
import google.generativeai as genai # type: ignore
from App.Commons.gemini_communication import GeminiCommunication

class DoubtAgent:
    def __init__(self):
        self.geminiCommunication = GeminiCommunication()

    def doubt_texter(self, user_input: str) -> str:
        prompt = f"""If the prompt is a programming query, return a response, which is Python specific without any markdown formatting or code fences.
        Else say irrelavant query. For example, 
        input: What command to print things?
        output: print() command
        input: What does cout do? 
        output: It's used to print to stdout in c++. Its equivalent in python is print()  
        input: what colour is a daisy? 
        output: Irrelavant query 
        prompt:{user_input}
        Also note that output should not be more then 50 words.
        Make sure you only give the output for the prompt"""
        response = self.geminiCommunication.send_prompt_to_gemini(prompt)
        # print(response)
        return response