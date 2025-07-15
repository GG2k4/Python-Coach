from sqlalchemy.orm import Session # type: ignore
from App.Commons.models import Users
from App.Commons.schemas import UserCreate, UserUpdate
from typing import List, Optional
from App.Commons.constants import basic_topics, topics_dimensions

class UserService:
    def __init__(self):
        # self.db = db
        pass

    def create_user(self, user: UserCreate, db: Session) -> Users:
        elo = user.elo
        for topic in basic_topics:
            if topic in topics_dimensions:
                elo[topics_dimensions[topic]] = 0.15
        db_user = Users(username=user.username, elo=elo, prompt_history=user.prompt_history)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_users(self, db: Session) -> List[Users]:
        return db.query(Users).all()

    def get_user_by_id(self, user_id: int, db: Session) -> Optional[Users]:
        try:
            return db.query(Users).filter(Users.id == user_id).first()
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_user_by_name(self, user_name: str, db: Session) -> Optional[Users]:
        return db.query(Users).filter(Users.username == user_name).first()

    def update_user_by_id(self, user: UserUpdate, db: Session) -> Optional[Users]:
        db_user = self.get_user_by_id(user.user_id, db)
        if db_user is None:
            return None
        if user.username:
            db_user.username = user.username
        if user.elo:
            db_user.elo = user.elo
        if user.prompt_history:
            db_user.prompt_history = user.prompt_history
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user_by_id(self, user_id: int, db: Session) -> bool:
        db_user = self.get_user_by_id(user_id)
        if db_user is None:
            return False
        db.delete(db_user)
        db.commit()
        return True