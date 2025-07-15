from App.Commons.models import AttemptedQuestion
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from App.Commons.schemas import AttemptedQuestionCreate, AttemptedQuestionGet, UserID
from App.Commons.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AttemptedQuestionService:
    def __init__(self):
        pass

    def create_new_attempted_question(self, attempted_question: AttemptedQuestionCreate, db: Session):
        db_attempted_question = AttemptedQuestion(user_id=attempted_question.user_id, question=attempted_question.question,
                                                  elo_value=attempted_question.elo_value, topics=attempted_question.topics)
        db.add(db_attempted_question)
        db.commit()
        db.refresh(db_attempted_question)
        return db_attempted_question
    
    def get_all_attempted_questions(self, user_id: UserID, db: Session):
        return db.query(AttemptedQuestion).filter(AttemptedQuestion.user_id == user_id.user_id).all()
    
    def remove_latest_attempted_question(self, user_id: UserID, db: Session):
        latest = db.query(AttemptedQuestion)\
                .filter(AttemptedQuestion.user_id == user_id.user_id)\
                .order_by(AttemptedQuestion.id.desc())\
                .first()
        if latest:
            db.delete(latest)
            db.commit()
            return True
        return False