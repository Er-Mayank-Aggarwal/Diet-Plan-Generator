import os
import json
import hashlib
import datetime
import re
import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt

# =================================================
# CONFIG
# =================================================
st.set_page_config(page_title="Smart Diet Planner", page_icon="🥗", layout="wide")

DATA_DIR = "data"
USERS_FILE = f"{DATA_DIR}/users.json"
HISTORY_FILE = f"{DATA_DIR}/history.json"
DIET_FILE = f"{DATA_DIR}/diet_plans.json"
os.makedirs(DATA_DIR, exist_ok=True)

TODAY_DATE = str(datetime.date.today())
TODAY_NAME = datetime.date.today().strftime("%A")

# =================================================
# SAFE JSON HELPERS
# =================================================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            txt = f.read().strip()
            if not txt:
                return default
            return json.loads(txt)
    except:
        return default

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
Return ONLY valid JSON.
Top-level keys: Monday to Sunday.
Each meal must have dish, standard_quantity, calories (number).

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
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group())
    except:
        return None

VALID_DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def normalize_diet(raw):
    if len(raw) == 1 and isinstance(list(raw.values())[0], dict):
        raw = list(raw.values())[0]

    final = {}
    for d in VALID_DAYS:
        meals = raw.get(d)
        if not isinstance(meals, list):
            continue
        clean = []
        for m in meals:
            dish = m.get("dish") or m.get("meal")
            qty = m.get("standard_quantity") or "1 serving"
            cal = m.get("calories") or m.get("kcal")
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
        st.error("Invalid AI diet output. Try again.")
        st.stop()
    return final

def generate_diet(user):
    client = get_client()
    for _ in range(2):
        res = client.GenerativeModel("gemini-2.5-flash").generate_content(build_prompt(user))
        raw = extract_json(res.text)
        if raw:
            return normalize_diet(raw)
    st.error("Diet generation failed.")
    st.stop()

# =================================================
# SESSION
# =================================================
for k in ["user", "diet", "show_diet_form"]:
    if k not in st.session_state:
        st.session_state[k] = None if k != "show_diet_form" else False

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
<div style="padding:15px;border-radius:12px;background:black;color:white;
display:flex;justify-content:space-between;">
<h2>🥗 Smart Diet Planner</h2>
<b>{st.session_state.user}</b>
</div>
""", unsafe_allow_html=True)

# =================================================
# SIDEBAR
# =================================================
with st.sidebar:
    if st.button("➕ Generate New Diet"):
        st.session_state.show_diet_form = True

# =================================================
# DIET FORM
# =================================================
if st.session_state.show_diet_form:
    st.markdown("## 🧾 Create New Diet Plan")

    with st.form("diet_form"):
        c1, c2 = st.columns(2)
        with c1:
            goal = st.selectbox("Goal", ["Lose", "Maintain", "Gain"])
            age = st.number_input("Age", 10, 80, 21)
            height = st.text_input("Height (cm)", "170")
        with c2:
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            gender = st.selectbox("Gender", ["Male", "Female"])
            diet = st.selectbox("Diet Preference", ["Veg", "Non-Veg", "Both"])
        activity = st.selectbox("Activity Level", ["Low", "Medium", "High"])

        submit = st.form_submit_button("Generate Diet")

    if submit:
        user = {
            "goal": goal, "age": age, "height": height,
            "weight": weight, "gender": gender,
            "diet": diet, "activity": activity
        }
        with st.spinner("Generating diet..."):
            st.session_state.diet = generate_diet(user)

        diets = load_json(DIET_FILE, {})
        diets[st.session_state.user] = st.session_state.diet
        save_json(DIET_FILE, diets)

        st.session_state.show_diet_form = False
        st.success("Diet generated successfully")
        st.rerun()

# =================================================
# TRACKER
# =================================================
if st.session_state.diet:
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("📅 Daily Diet View")
        day = st.selectbox("Select Day", list(st.session_state.diet.keys()))
        is_today = (day == TODAY_NAME)

        planned = sum(m["calories"] for m in st.session_state.diet[day])
        consumed = 0

        for i, m in enumerate(st.session_state.diet[day]):
            a,b,c = st.columns([4,2,2])
            with a:
                st.write(f"{m['dish']} ({m['standard_quantity']})")
            with b:
                if is_today:
                    qty = st.number_input("Qty", 0.0, 5.0, 1.0, 0.5, key=f"{day}_q{i}")
                    eaten = st.checkbox("Eaten", key=f"{day}_e{i}")
                else:
                    qty, eaten = 1, False
            with c:
                st.write(f"{m['calories']} kcal")
            if is_today and eaten:
                consumed += m["calories"] * qty

    with col2:
        st.subheader("📊 Summary")
        remaining = max(0, planned - consumed)

        st.metric("Planned", planned)
        st.metric("Consumed", int(consumed))
        st.metric("Remaining", int(remaining))

        if is_today and remaining <= 20:
            st.success("🏅 Perfect Day Completed!")

        if is_today and st.button("Save / Update Today"):
            history = load_json(HISTORY_FILE, {})
            history.setdefault(st.session_state.user, {})
            history[st.session_state.user][TODAY_DATE] = {
                "day": day, "planned": planned, "consumed": int(consumed)
            }
            save_json(HISTORY_FILE, history)
            st.success("Saved")

# =================================================
# HISTORY
# =================================================
st.markdown("---")
st.subheader("📜 History")

hist = load_json(HISTORY_FILE, {}).get(st.session_state.user, {})
if hist:
    st.dataframe([{"date": d, **v} for d, v in hist.items()], use_container_width=True)
else:
    st.info("No history yet")

# =================================================
# WEEKLY CHART
# =================================================
st.markdown("---")
st.subheader("📈 Weekly Calories Overview")

if hist:
    df = pd.DataFrame.from_dict(hist, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().tail(7)

    fig, ax = plt.subplots()
    ax.plot(df.index.strftime("%a"), df["planned"], marker="o", label="Planned")
    ax.plot(df.index.strftime("%a"), df["consumed"], marker="o", label="Consumed")
    ax.legend()
    ax.set_ylabel("Calories")
    st.pyplot(fig)
