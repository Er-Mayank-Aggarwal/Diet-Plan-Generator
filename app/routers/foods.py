from fastapi import APIRouter, Request
from app.db.crud import get_foods
from app.db.crud import USERS

router = APIRouter()

@router.get("/")
def food_list(request: Request):
    email = request.state.user_email
    user = USERS.get(email)

    if not user:
        return {"detail": "User profile not found"}

    return get_foods(user["food_preference"])
