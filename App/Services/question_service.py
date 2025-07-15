from App.Services.user_service import UserService
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from App.Commons.schemas import QuestionRequest, QuestionResponse
from App.DB.questions_query import queryDB

class QuestionService:
    def __init__(self):
        self.query_db = queryDB()
        self.user_service = UserService()
    
    def get_question(self, request: QuestionRequest, db: Session):
        if request.use_elo:
            elo = self.user_service.get_user_by_id(user_id=request.user_id, db=db).elo
            question_vector, question, topics = self.query_db.get_question(user_id=request.user_id, query_weights_vector=elo, db=db)
        else:
            (question_vector, question, topics), elo = self.query_db.get_question_by_topic(request.user_id,  request.topics, db)
        return QuestionResponse(question=question, topics=topics, vector=question_vector, elo=elo)
        