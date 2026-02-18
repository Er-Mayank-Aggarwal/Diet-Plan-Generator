from pydantic import BaseModel
from typing import Dict, List

class MealItem(BaseModel):
    food: str
    quantity: int

class DayPlan(BaseModel):
    Breakfast: List[MealItem]
    Lunch: List[MealItem]
    Dinner: List[MealItem]

class WeeklyPlan(BaseModel):
    Monday: DayPlan
    Tuesday: DayPlan
    Wednesday: DayPlan
    Thursday: DayPlan
    Friday: DayPlan
    Saturday: DayPlan
    Sunday: DayPlan
