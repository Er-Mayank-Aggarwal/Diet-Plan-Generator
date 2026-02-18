from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/")
def add_favorite(food: dict, request: Request):
    return {
        "message": "Added to favorites",
        "food": food
    }
