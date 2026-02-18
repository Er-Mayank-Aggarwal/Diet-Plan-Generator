from fastapi import APIRouter, Request
from app.schemas.user import UserProfile
from app.schemas.journey import UserJourney
from app.db.crud import save_user, save_journey

router = APIRouter()

@router.post("/profile")
def user_profile(data: UserProfile, request: Request):
    save_user(request.state.user_email, data.dict())
    return {"msg": "Profile saved"}

@router.post("/journey")
def user_journey(data: UserJourney, request: Request):
    save_journey(request.state.user_email, data.dict())
    return {"msg": "Journey saved"}
