from fastapi import APIRouter
from src.schemas import UserSchema

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserSchema, summary="Получить текущего пользователя")
async def get_current_user():
    return UserSchema()
