import os
import json
import hashlib
import datetime
import re
import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import pytz


# =================================================
# CONFIG
# =================================================
st.set_page_config(
    page_title="Smart Diet Planner",
    page_icon="🥗",
    layout="wide"
)

DATA_DIR = "data"
USERS_FILE = f"{DATA_DIR}/users.json"
HISTORY_FILE = f"{DATA_DIR}/history.json"
DIET_FILE = f"{DATA_DIR}/diet_plans.json"
os.makedirs(DATA_DIR, exist_ok=True)

IST = pytz.timezone("Asia/Kolkata")
now_ist = datetime.datetime.now(IST)

TODAY_DATE = now_ist.date().isoformat()
TODAY_NAME = now_ist.strftime("%A")


# =================================================
# HELPERS
# =================================================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# =================================================
# AUTH
# =================================================
def signup(email, password):
    users = load_json(USERS_FILE, {})
    if email in users:
        return False
    users[email] = hash_password(password)
    save_json(USERS_FILE, users)
    return True

def login(email, password):
    users = load_json(USERS_FILE, {})
    return email in users and users[email] == hash_password(password)

# =================================================
# GEMINI
# =================================================
def get_client():
    api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY not set")
        st.stop()
    genai.configure(api_key=api_key)
    return genai

def build_prompt(user):
    return f"""
STRICT RULES:
- Return ONLY valid JSON
- NO wrapper keys
- Top-level keys must be weekdays (Monday–Sunday)
- Each day must be a list
- Each meal must have: dish, standard_quantity, calories (number)

User:
Goal: {user['goal']}
Age: {user['age']}
Height: {user['height']}
Weight: {user['weight']}
Gender: {user['gender']}
Diet: {user['diet']}
Activity: {user['activity']}
"""

def extract_json(text):
    text = text.replace("```json", "").replace("```", "")
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except:
        return None

VALID_DAYS = [
    "Monday","Tuesday","Wednesday",
    "Thursday","Friday","Saturday","Sunday"
]

def normalize_diet_plan(raw):
    if len(raw) == 1 and isinstance(list(raw.values())[0], dict):
        raw = list(raw.values())[0]

    final = {}
    for d in VALID_DAYS:
        meals = raw.get(d)
        if not isinstance(meals, list):
            continue

        clean = []
        for m in meals:
            dish = m.get("dish") or m.get("meal") or m.get("item")
            qty = m.get("standard_quantity") or m.get("quantity") or "1 serving"
            cal = m.get("calories") or m.get("kcal") or m.get("cal")
            try:
                cal = int(str(cal).replace("kcal", "").strip())
            except:
                continue

            if dish and cal > 0:
                clean.append({
                    "dish": dish,
                    "standard_quantity": qty,
                    "calories": cal
                })

        if clean:
            final[d] = clean

    if not final:
        st.error("AI diet invalid. Try again.")
        st.stop()

    return final

def generate_diet(user):
    client = get_client()
    for _ in range(2):
        res = client.GenerativeModel("gemini-2.5-flash").generate_content(build_prompt(user))
        raw = extract_json(res.text)
        if raw:
            return normalize_diet_plan(raw)
    st.error("Diet generation failed.")
    st.stop()

# =================================================
# SESSION
# =================================================
for k in ["user", "diet"]:
    if k not in st.session_state:
        st.session_state[k] = None

# =================================================
# AUTH UI
# =================================================
if not st.session_state.user:
    st.title("🥗 Smart Diet Planner")

    t1, t2 = st.tabs(["Login", "Sign Up"])

    with t1:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(email, pwd):
                st.session_state.user = email
                st.session_state.diet = load_json(DIET_FILE, {}).get(email)
                st.rerun()
            else:
                st.error("Invalid credentials")

    with t2:
        email = st.text_input("New Email")
        pwd = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if signup(email, pwd):
                st.success("Account created. Login now.")
            else:
                st.error("User already exists")

    st.stop()

# =================================================
# HEADER
# =================================================
st.markdown(f"""
<div style="padding:15px;border-radius:12px;
background:black;color:white;
display:flex;justify-content:space-between;">
<h2>🥗 Smart Diet Planner</h2>
<b>{st.session_state.user}</b>
</div>
""", unsafe_allow_html=True)

# =================================================
# SIDEBAR
# =================================================
with st.sidebar:
    st.markdown("### ⚙ Profile")

    if st.button("Generate New Diet"):
        user = {
            "goal": "Maintain",
            "age": 21,
            "height": "170",
            "weight": 70,
            "gender": "Male",
            "diet": "Veg",
            "activity": "Medium"
        }
        st.session_state.diet = generate_diet(user)
        diets = load_json(DIET_FILE, {})
        diets[st.session_state.user] = st.session_state.diet
        save_json(DIET_FILE, diets)

# =================================================
# TRACKER
# =================================================
if st.session_state.diet:
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("📅 Daily Diet View")
        day = st.selectbox("Select Day", list(st.session_state.diet.keys()))

        is_today = (day == TODAY_NAME)

        if is_today:
            st.success("🟢 Today — Track your meals")
        else:
            st.info("🔒 Past Day — Read only")

        planned = sum(m["calories"] for m in st.session_state.diet[day])
        consumed = 0

        for i, m in enumerate(st.session_state.diet[day]):
            a,b,c = st.columns([4,2,2])
            with a:
                st.write(f"🍽️ {m['dish']} ({m['standard_quantity']})")
            with b:
                if is_today:
                    qty = st.number_input(
                        "Quanty you ate", 0.0, 5.0, 1.0, 0.5,
                        key=f"{day}_q{i}"
                    )
                    eaten = st.checkbox("Eaten", key=f"{day}_e{i}")
                else:
                    qty = 1
                    eaten = False
            with c:
                st.write(f"🔥 {m['calories']} kcal")

            if is_today and eaten:
                consumed += m["calories"] * qty

    with col2:
        st.subheader("📊 Summary")

        if is_today:
            remaining = max(0, planned - consumed)

            st.metric("📋 Planned", planned)
            st.metric("🔥 Consumed", int(consumed))
            st.metric("⏳ Remaining", int(remaining))

            if remaining <= 20:
                st.success("🏅 Perfect Day Completed!")

            if st.button("💾 Save / Update Today"):
                history = load_json(HISTORY_FILE, {})
                history.setdefault(st.session_state.user, {})
                history[st.session_state.user][TODAY_DATE] = {
                    "day": day,
                    "planned": planned,
                    "consumed": int(consumed)
                }
                save_json(HISTORY_FILE, history)
                st.success("Saved")

        else:
            hist = load_json(HISTORY_FILE, {}).get(st.session_state.user, {})
            record = hist.get(
                next((d for d, v in hist.items() if v["day"] == day), None)
            )

            if record:
                st.metric("📋 Planned", record["planned"])
                st.metric("🔥 Consumed", record["consumed"])
            else:
                st.info("No data saved for this day")

# =================================================
# HISTORY
# =================================================
st.markdown("---")
st.subheader("📜 History")

hist = load_json(HISTORY_FILE, {}).get(st.session_state.user, {})
if hist:
    rows = [{"date": d, **v} for d, v in hist.items()]
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No history yet")

# =================================================
# WEEKLY CHART
# =================================================
st.markdown("---")
st.subheader("📈 Weekly Calories Overview")

hist = load_json(HISTORY_FILE, {}).get(st.session_state.user, {})

if hist:
    # Convert history dict → DataFrame
    df = pd.DataFrame.from_dict(hist, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Last 7 days only
    last_7 = df.tail(7)

    if not last_7.empty:
        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(
            last_7.index.strftime("%a"),
            last_7["planned"],
            marker="o",
            label="Planned",
            linewidth=2
        )

        ax.plot(
            last_7.index.strftime("%a"),
            last_7["consumed"],
            marker="o",
            label="Consumed",
            linewidth=2
        )

        ax.set_ylabel("Calories")
        ax.set_title("Last 7 Days Calories")
        ax.legend()
        ax.grid(alpha=0.3)

        st.pyplot(fig)
    else:
        st.info("Not enough data for weekly chart yet.")
else:
    st.info("Save daily data to see weekly progress.")
