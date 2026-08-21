from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/frontend-api/users/me")
def get_user_me():
    return {
        "email": "user@example.com",
        "isActive": True,
        "profileId": "1",
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2025-06-15T18:29:56+00:00",
        "username": "superuser",
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
