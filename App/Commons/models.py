from sqlalchemy import Column, Integer, String, JSON, ForeignKey # type: ignore
from App.Commons.database import Base, engine
    
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    elo = Column(JSON, nullable=False)
    prompt_history = Column(String, nullable=True)

class AttemptedQuestion(Base):
    __tablename__ = 'attempted_questions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(String, nullable=False)
    elo_value = Column(JSON, nullable=False)
    topics = Column(JSON, nullable=False)