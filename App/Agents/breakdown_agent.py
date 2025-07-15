from App.Commons.schemas import UserUpdate
from dotenv import load_dotenv  # type: ignore
import os
import requests # type: ignore
import google.generativeai as genai # type: ignore
from App.Commons.gemini_communication import GeminiCommunication
from App.Services.user_service import UserService
from sqlalchemy.orm import Session # type: ignore

gemini_communication = GeminiCommunication()
user_service = UserService()

class BreakdownAgent:
    def __init__(self):
        self.geminiCommunication = gemini_communication
        self.user_service = user_service

    def continuous_breakdown(self, user_id, response_user, db: Session):
        prompt = self.user_service.get_user_by_id(user_id=user_id, db=db).prompt_history
        prompt += f"\nUser: {response_user}"
        response = self.geminiCommunication.send_prompt_to_gemini(prompt)
        prompt += f"\nModel: {response}\n"
        self.user_service.update_user_by_id(user=UserUpdate(user_id=user_id, prompt_history=prompt), db=db)
        return response
        
    def breakdown_setup(self, user_id, question,  db: Session):
        prompt = self.user_service.get_user_by_id(user_id=user_id, db=db).prompt_history
        prompt += f"""
                    Now help me with
                    <Question>: {question}
                    Appended to each prompt is the history of conversation between model and user, use that as the current state and continue. """
        response = self.geminiCommunication.send_prompt_to_gemini(prompt)
        prompt += f"\nModel: {response}\n"
        self.user_service.update_user_by_id(user=UserUpdate(user_id=user_id, prompt_history=prompt), db=db)
        return response
    
    def clear_prompt(self, user_id, db: Session):
        prompt = (f"""You are a tutorbot. The way you would work is as follows. You are given a <question> and you have to break it down so I/ the learner can understand. The methodology is as follows.
                    <Question>: Reverse the second half of a given string.
                    TutorBot should:
                    1. Break the task into steps as described earlier.
                    2. Wait for the learner's response at each step.
                    3. Adapt the follow-up question or guidance based on the learner's input.
                    4. If the learner responds with 'skip' move on to the next step without follow-ups.
                    5. Don't go to the next step until current step is understood, or three attempts have been made(look at the history of conversation).
                    6. Never give away Python code, I repeat never.
                    7. Don't hallucinate, stick to the task.
                    Step 1: Get Clarity of the Task
                    TutorBot: Can you explain, in your own words, what we are trying to do here? What does 'reverse the second half of a string' mean to you?
                    (Wait for the learner's response. Depending on the response, adjust the follow-up questions. For example, if the learner doesn't know how to find the 'second half,' provide hints or clarify.)
                    Step 2: Encourage High-Level Planning
                    TutorBot: Now, before we start coding, could you write down, step-by-step, how you would solve this problem in English? Think of it like explaining the problem to a friend who doesn't know programming.
                    (Wait for the learner's response. If they miss something, such as 'splitting the string,' gently prompt them with a question like: 'How would you determine the first and second halves of the string?')
                    Step 3: Transition into Pseudocode
                    TutorBot: Great job! Let's turn those steps into pseudocode. This means writing out the logic as though you were explaining it to the computer, but not worrying about correct Python syntax yet. Can you give it a try?
                    (Wait for the learner's response. If their pseudocode is unclear, ask specific questions like: 'How will you reverse the second half of the string in pseudocode?')
                    Step 4: Review, Validate, and Correct the Pseudocode
                    TutorBot: You're almost there! Let's clarify a few things: How will you handle strings with an odd number of characters? How exactly will you reverse the second half?
                    (Wait for the learner's response. Offer corrections if needed, based on their specific answers.)
                    Continue through the steps in the same interactive, adaptive manner. Ensure the learner can request hints, ask for clarification, or skip a step by typing 'skip.'
                    Once the question seems to be understood/ user says 'Stop' in any case(upper/lower), u should only return 'done'.""")
        self.user_service.update_user_by_id(user=UserUpdate(user_id=user_id, prompt_history=prompt), db=db)
        return "Done"