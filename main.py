from App.Routes.user_routes import UserRoutes
from App.Routes.question_routes import QuestionRoutes
from fastapi import FastAPI # type: ignore
import uvicorn # type: ignore
import sys
import os
from fastapi.middleware.cors import CORSMiddleware # type: ignore

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

question_routes = QuestionRoutes()
user_routes = UserRoutes()

app.include_router(question_routes.router, prefix='/api')
app.include_router(user_routes.router, prefix='/api')

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI App!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)