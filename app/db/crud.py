from datetime import date

USERS = {}
JOURNEY = {}
DAILY_INTAKE = {}
FAVORITES = {}
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "diets.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    FOODS = json.load(f)


# USER
def save_user(email, data): USERS[email] = data
def save_journey(email, data): JOURNEY[email] = data

# INTAKE
def save_intake(email, date, totals): DAILY_INTAKE[(email, date)] = totals
def get_intake(email, date): return DAILY_INTAKE.get((email, date))

def last_7_days(email):
    return [v["calories"] for (e, _), v in DAILY_INTAKE.items() if e == email][-7:]

# FAVORITES
def add_fav(email, food):
    FAVORITES.setdefault(email, [])
    if len(FAVORITES[email]) < 10:
        FAVORITES[email].append(food)

# FOODS
def get_foods(food_preference: str):
    """
    food_preference: veg | nonveg | both | egg_only
    """
    if food_preference == "veg":
        return [f for f in FOODS if f["category"] == "veg"]

    if food_preference == "nonveg":
        return [f for f in FOODS if f["category"] == "nonveg"]

    if food_preference == "egg_only":
        return [f for f in FOODS if f["category"] == "egg"]

    return FOODS  # both

