from fastapi.params import Query # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    username: str
    elo: list = [0.0]*115
    prompt_history: str = f"""You are a tutorbot. The way you would work is as follows. You are given a <question> and you have to break it down so I/ the learner can understand. The methodology is as follows.
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
                    Once the question seems to be understood/ user says 'Stop' in any case(upper/lower), u should only return 'done'."""

class UserGet(BaseModel):
    id: int
    username: str
    elo: list
    prompt_history: str
    class Config:
        from_attributes  = True

class UserUpdate(BaseModel):
    user_id: int
    username: Optional[str] = None
    elo: Optional[list] = None
    prompt_history: Optional[str] = None

class QuestionRequest(BaseModel):
    use_elo: bool
    user_id: int
    topics: Optional[Dict[str, float]] = None

class QuestionResponse(BaseModel):
    question: str
    topics: Dict[str, float]
    vector: List[float]
    elo: list

class BreakdownRequest(BaseModel):
    user_id: int
    question: str
    user_response: Optional[str] = None

class EloUpdateRequest(BaseModel):
    user_id: int
    question_response: QuestionResponse
    scores: dict
    decay: float = 0.9

class FeedbackRequest(BaseModel):
    question: str
    code: str 

class EvalRequest(BaseModel):
    question_response: QuestionResponse
    code: str

class SetupRequest(BaseModel):
    user_id: int
    question: str

class UserID(BaseModel):
    user_id: int

class AttemptedQuestionCreate(BaseModel):
    user_id: int
    question: str
    elo_value: list
    topics: dict

class AttemptedQuestionGet(BaseModel):
    user_id: int
    id: int
    question: str
    elo_value: list
    topics: dict

class Username(BaseModel):
    user_name: str = Query(description="Query by Username")

class DoubtRequest(BaseModel):
    user_input: str