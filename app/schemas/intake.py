from pydantic import BaseModel

class IntakeTotals(BaseModel):
    protein: int
    carbs: int
    fat: int
    calories: int

class IntakeRequest(BaseModel):
    date: str
    totals: IntakeTotals
