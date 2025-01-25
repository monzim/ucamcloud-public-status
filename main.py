from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="User Management API",
    description="A robust API for user management operations",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)


class UserCreate(BaseModel):
    """User creation request model"""
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    email: EmailStr = Field(..., example="john@example.com")
    age: int = Field(..., gt=0, example=25)

    class Config:
        schema_extra = {
            "example": {
                "username": "jane_doe",
                "email": "jane@example.com",
                "age": 28
            }
        }


class UserResponse(UserCreate):
    """User response model"""
    pass


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str


# In-memory database with username index
users_db = {}
usernames = set()


@app.get(
    "/",
    summary="Service Health Check",
    response_description="Basic service status response",
    tags=["Service Health"]
)
async def health_check():
    """
    Returns basic service status information.

    This endpoint provides a quick verification that the API is operational.
    """
    return {"message": "Service operational"}


@app.post(
    "/users/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse}
    },
    summary="Create a new user",
    tags=["User Management"]
)
async def create_user(user: UserCreate):
    """
    Creates a new user with the provided information.

    - **username**: must be unique and between 3-50 characters
    - **email**: must be a valid email format
    - **age**: must be a positive integer
    """
    if user.username in usernames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    user_data = user.dict()
    users_db[user.username] = user_data
    usernames.add(user.username)
    return user_data


@app.get(
    "/users/",
    response_model=dict[str, list[UserResponse]],
    summary="List all users",
    tags=["User Management"]
)
async def list_users():
    """Returns a list of all registered users"""
    return {"users": list(users_db.values())}


@app.get(
    "/users/{username}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse}
    },
    summary="Get user by username",
    tags=["User Management"]
)
async def get_user(username: str):
    """Retrieves detailed information for a specific user by username"""
    user = users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user