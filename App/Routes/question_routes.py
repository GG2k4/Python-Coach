import json
from App.Agents.breakdown_agent import BreakdownAgent
from App.Agents.eval_agent import EvalAgent
from App.Agents.feedback_agent import FeedbackAgent
from App.Agents.doubt_agent import DoubtAgent
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import List, Annotated, Dict
from App.Commons.database import SessionLocal
from App.Commons.schemas import QuestionRequest, QuestionResponse, BreakdownRequest, FeedbackRequest, EvalRequest, SetupRequest, UserID, DoubtRequest
from App.Services.question_service import QuestionService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# db_dependency = Annotated[Session, Depends(get_db)]
question_service = QuestionService()
breakdown_agent = BreakdownAgent()
feedback_agent = FeedbackAgent()
eval_agent = EvalAgent()
doubt_agent = DoubtAgent()

router = APIRouter()

class QuestionRoutes:
    def __init__(self):
        self.question_service = question_service
        self.breakdown_agent = breakdown_agent
        self.feedback_agent = feedback_agent
        self.eval_agent = eval_agent
        self.doubt_agent = doubt_agent
        self.router = router
        self.setup_routes()

    def setup_routes(self):
        self.router.post("/questions/", response_model=QuestionResponse)(self.get_question)
        self.router.put("/questions/breakdown_setup", response_model=str)(self.breakdown_question)
        self.router.put("/questions/breakdown", response_model=str)(self.breakdown_question_continuous)
        self.router.put("/questions/breakdown_clear", response_model=str)(self.breakdown_clear)
        self.router.post("/questions/eval", response_model=dict)(self.eval)
        self.router.post("/questions/feedback", response_model=str)(self.feedback)
        self.router.post("/questions/doubt", response_model=str)(self.doubt)


    async def get_question(self, request: QuestionRequest, db: Session = Depends(get_db)):
        question_data = self.question_service.get_question(request, db)
        if not question_data:
            raise HTTPException(status_code=404, detail="No suitable question found")
        return question_data
    
    async def breakdown_question(self, question: SetupRequest, db: Session = Depends(get_db)):
        return self.breakdown_agent.breakdown_setup(question=question.question, db=db, user_id=question.user_id)

    async def breakdown_question_continuous(self, response: BreakdownRequest, db: Session = Depends(get_db)):
        return self.breakdown_agent.continuous_breakdown(response_user=response.user_response, db=db, user_id=response.user_id)
    
    async def breakdown_clear(self, user: UserID, db: Session = Depends(get_db)):
        return self.breakdown_agent.clear_prompt(db=db, user_id=user.user_id)
    
    async def eval(self, eval_request: EvalRequest):
        result = await self.eval_agent.get_llm_score(
            question=eval_request.question_response.question,
            code=eval_request.code,
            topics=list(eval_request.question_response.topics.keys())
        )
        return result
    
    async def feedback(self, feedback_request: FeedbackRequest):
        return self.feedback_agent.get_llm_feedback(question=feedback_request.question, code=feedback_request.code)
    
    async def doubt(self, doubt_request: DoubtRequest):
        return doubt_agent.doubt_texter(doubt_request.user_input)