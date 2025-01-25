from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastAPI Basics")

class User(BaseModel):
    username: str
    email: str
    age: int

users_db = []

@app.post("/users/")
def create_user(user: User):
    if user.username in [u["username"] for u in users_db]:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db.append(user.dict())
    return {"message": "User created successfully", "user": user}

@app.get("/users/")
def list_users():
    return {"users": users_db}

@app.get("/users/{username}")
def get_user(username: str):
    user = next((u for u in users_db if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

app = FastAPI(
    title="My FastAPI App",
    description="A sample API for learning FastAPI",
    version="1.0.0"
)
