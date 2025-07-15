from dotenv import load_dotenv  # type: ignore
import os
import requests # type: ignore
import google.generativeai as genai # type: ignore
from App.Commons.gemini_communication import GeminiCommunication

class FeedbackAgent:
    def __init__(self):
        self.geminiCommunication = GeminiCommunication()

    def get_llm_feedback(self, question, code) -> str:
        prompt = f"""
You are an expert Python code reviewer. Provide concise and detailed feedback on the following Python code (response to the question: "{question}"). Your feedback should cover these sections:
- Correctness: Briefly state if the code solves the problem correctly, note any bugs or edge cases.
- Efficiency: Summarize time/space complexity and potential optimizations.
- Code Style and Readability: Comment on PEP 8 adherence, naming, and clarity.
- Best Practices: Mention error handling, modularity, and any anti-patterns.
- Suggestions for Improvement: List 2-3 specific, actionable improvements.
Present your feedback in bullet points and limit the overall response to 200 words. Do not include extraneous text or markdown formatting beyond bullet points.

Code:
```python
{code}
```
"""
        response = self.geminiCommunication.send_prompt_to_gemini(prompt)
        return response