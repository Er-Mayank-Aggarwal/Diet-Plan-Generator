from pydantic import BaseModel

class UserJourney(BaseModel):
    goal: str
    fitness_level: str
