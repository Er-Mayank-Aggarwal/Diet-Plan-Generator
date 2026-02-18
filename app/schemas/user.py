from pydantic import BaseModel

class UserProfile(BaseModel):
    height_cm: int
    weight_kg: int
    dob: str
    gender: str
    food_preference: str
