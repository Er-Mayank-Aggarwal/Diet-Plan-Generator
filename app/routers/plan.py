from fastapi import APIRouter, Request, HTTPException
from app.services.plan_service import generate_diet_plan
from app.db.crud import USERS, JOURNEY

router = APIRouter()

@router.post("/generate")
def generate_plan(request: Request):
    email = request.state.user_email

    user_profile = USERS.get(email)
    journey = JOURNEY.get(email)

    if not user_profile:
        raise HTTPException(status_code=400, detail="User profile not found")

    if not journey:
        raise HTTPException(status_code=400, detail="User journey not found")

    try:
        plan = generate_diet_plan(user_profile, journey)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "email": email,
        "plan": plan
    }
