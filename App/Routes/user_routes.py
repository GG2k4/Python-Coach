from fastapi.params import Query # type: ignore
from App.DB.questions_query import queryDB
from fastapi import APIRouter, HTTPException, Depends # type: ignore
from App.Commons.schemas import UserCreate, UserGet, UserID, UserUpdate, EloUpdateRequest, Username
from App.Services.user_service import UserService
from sqlalchemy.orm import Session # type: ignore
from App.Commons.database import SessionLocal
from typing import List, Annotated
from App.Commons.constants import topics_dimensions, basic_topics, advanced_topics

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter()
user_service = UserService()
query_db = queryDB()

class UserRoutes:
    def __init__(self):
        self.user_service = user_service
        self.router = router
        self.query_db = query_db
        self.setup_routes()

    def setup_routes(self):
        self.router.post("/users", response_model=UserGet)(self.create_user)
        # self.router.get("/users/", response_model=List[UserGet])(self.get_users)
        self.router.get("/users/{user_id}", response_model=UserGet)(self.get_user_by_id)
        # self.router.put("/users/{user_id}", response_model=UserGet)(self.update_user_by_id)
        # self.router.delete("/users/{user_id}")(self.delete_user_by_id)
        self.router.put("/users/{user_id}/elo", response_model=UserGet)(self.update_elo)
        self.router.get("/users", response_model=UserGet)(self.get_user_by_name)

    async def create_user(self, user: UserCreate, db: Session = Depends(get_db)):
        return self.user_service.create_user(user, db)

    # async def get_users(self, db = db_dependency):
    #     return self.user_service.get_users(db)

    async def get_user_by_id(self, user_id: int, db: Session = Depends(get_db)):
        user = self.user_service.get_user_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def get_user_by_name(self, user_name: str = Query(), db: Session = Depends(get_db)):
        user = self.user_service.get_user_by_name(user_name, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # async def update_user_by_id(self, user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    #     updated_user = self.user_service.update_user_by_id(user_id, user, db)
    #     if updated_user is None:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return updated_user

    # async def delete_user_by_id(self, user_id: int, db = db_dependency):
    #     if not self.user_service.delete_user_by_id(user_id, db):
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return {"message": "User deleted successfully"}
    
    async def update_elo(self, elo_update_request: EloUpdateRequest, db: Session = Depends(get_db)):
        scores_dict = elo_update_request.scores
        avg_score = sum(scores_dict.values()) / len(scores_dict) if scores_dict else 0
        threshold = 0.6
        if avg_score < threshold:
            self.query_db.attempted_question_service.remove_latest_attempted_question(
                user_id=UserID(user_id=elo_update_request.user_id),
                db=db
            )

        learning_rates = [1.0] * 115
        for topic in basic_topics:
            if topic in topics_dimensions:
                learning_rates[topics_dimensions[topic]] = 1.1
        for topic in advanced_topics:
            if topic in topics_dimensions:
                learning_rates[topics_dimensions[topic]] = 0.8

        score = self.query_db.create_topic_vector(elo_update_request.scores)
        elo = self.user_service.get_user_by_id(user_id=elo_update_request.user_id, db=db).elo
        updatedelo = []
        n=len(elo)
        if elo==[0.0]*115:
            for i in range(n):
                a=elo_update_request.question_response.vector[i]
                b=score[i]
                updatedelo.append(a*b*elo_update_request.decay*learning_rates[i])
        else:
            for i in range(n):
                a=elo[i]
                b=elo_update_request.question_response.vector[i]
                c=score[i]
                d=elo_update_request.question_response.elo[i]
                updatedelo.append(a + elo_update_request.decay * (b*c - min(d,b)) * learning_rates[i])
        updated_user = self.user_service.update_user_by_id(UserUpdate(user_id=elo_update_request.user_id, elo=updatedelo), db)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user