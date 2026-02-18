import json
import re
import google.generativeai as genai
from app.db.crud import get_foods


# ---------- Helper: extract JSON safely ----------
def extract_json(text: str) -> dict:
    """
    Gemini sometimes adds text around JSON.
    This extracts the first valid JSON object.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("Gemini response did not contain valid JSON")
    return json.loads(match.group())


# ---------- Prompt Builder ----------
def build_prompt(user_profile: dict, journey: dict, foods: list) -> str:
    food_names = [f["name"] for f in foods]

    return f"""
You are a STRICT diet planning API.

RULES (DO NOT BREAK):
- OUTPUT ONLY VALID JSON
- NO explanations, NO markdown
- Each day MUST have Breakfast, Lunch, Dinner
- Each meal MUST have at least ONE item
- Use ONLY foods from this list:
{food_names}

User profile:
- Weight: {user_profile["weight_kg"]} kg
- Height: {user_profile["height_cm"]} cm
- Gender: {user_profile["gender"]}
- Food preference: {user_profile["food_preference"]}

User goal:
- Goal: {journey["goal"]}
- Fitness level: {journey["fitness_level"]}

REQUIRED FORMAT:
{{
  "Monday": {{
    "Breakfast": [{{"food": "Idli", calories": 150, protein": 4, carbs": 30, fat": 1}}],
    "Lunch": [{{"food": "Dal", calories": 150, protein": 4, carbs": 30, fat": 1}}],
    "Dinner": [{{"food": "Dal", calories": 150, protein": 4, carbs": 30, fat": 1}}]
  }},
  "Tuesday": {{ "Breakfast": [], "Lunch": [], "Dinner": [] }},
  "Wednesday": {{ "Breakfast": [], "Lunch": [], "Dinner": [] }},
  "Thursday": {{ "Breakfast": [], "Lunch": [], "Dinner": [] }},
  "Friday": {{ "Breakfast": [], "Lunch": [], "Dinner": [] }},
  "Saturday": {{ "Breakfast": [], "Lunch": [], "Dinner": [] }},
  "Sunday": {{ "Breakfast": [], "Lunch": [], "Dinner": [] }}
}}
"""


# ---------- Main Gemini Service ----------
def generate_diet_plan(user_profile: dict, journey: dict) -> dict:
    foods = get_foods(user_profile["food_preference"])

    prompt = build_prompt(user_profile, journey, foods)

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    plan = extract_json(response.text)

    return plan
