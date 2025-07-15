import re
from starlette.concurrency import run_in_threadpool
from App.Commons.gemini_communication import GeminiCommunication

class EvalAgent:
    def __init__(self):
        self.geminiCommunication = GeminiCommunication()

    async def get_llm_score(self, question, code, topics):
        # Updated prompt that instructs Gemini to output only a Python list with no extra text
        prompt = f"""
The following Python code was submitted in response to the question: "{question}".
Code: {code}

The topics are {topics}.
For each topic, provide a grade out of 10.
Return ONLY a Python list of integers in the exact format below with no additional text, markdown formatting, or code blocks:
Example: [5, 6, 3, 9, 8, 4, 2]

If the code appears to have issues, lower scores should be given.
"""
        # print("EvalAgent: Sending prompt to Gemini")
        response = await run_in_threadpool(self.geminiCommunication.send_prompt_to_gemini, prompt)
        # print("EvalAgent: Received response from Gemini:", response)

        list_match = re.search(r'\[(?:\s*\d+\s*(?:,\s*\d+\s*)*)\]', response)
        if list_match:
            list_str = list_match.group(0)
            numbers = re.findall(r'\d+', list_str)
            topic_scores = [int(num) for num in numbers]
        else:
            topic_scores = []

        topic_scores_dict = {}
        for ind, topic in enumerate(topics):
            score = topic_scores[ind] if ind < len(topic_scores) else 0
            topic_scores_dict[topic] = score / 10.0

        return topic_scores_dict
