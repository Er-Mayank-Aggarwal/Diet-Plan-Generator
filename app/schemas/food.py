from pydantic import BaseModel

class Food(BaseModel):
    id: int
    name: str
    protein: int
    carbs: int
    fat: int
    calories: int
    type: str
    category: str
    meal: str
