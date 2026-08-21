from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr

app = FastAPI()


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profileId: str
    email: EmailStr
    username: str
    isActive: bool
    registeredAt: datetime
    updatedAt: datetime


@app.get("/frontend-api/users/me", response_model=UserProfileSchema)
def get_user_me() -> UserProfileSchema:
    return {
        "email": "example@example.com",
        "isActive": True,
        "profileId": "1",
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2025-06-15T18:29:56+00:00",
        "username": "user123",
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
