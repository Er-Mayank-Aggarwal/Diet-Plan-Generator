import os
import streamlit as st
import google.generativeai as genai


st.set_page_config(page_title="Smart Diet Planner", page_icon="🥗")

st.markdown("""
<style>
a.anchor-link {
    display: none !important;
}

textarea {
    resize: none !important;
}

input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none !important;
    margin: 0 !important;
}

input[type=number] {
    -moz-appearance: textfield !important;
}

div[data-testid="stNumberInput"] button {
    display: none !important;
}

div[data-baseweb="select"] input,
div[data-testid="stSelectbox"],
div[data-testid="stSelectbox"] * ,
div[role="radiogroup"] label,
div[data-testid="stRadio"] label {
    cursor: pointer !important;
    caret-color: transparent !important;
    user-select: none !important;
}

[data-testid="stHelp"] {
    display: none !important;
}
</style>

<script>
(function() {
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      const el = document.activeElement;
      if (!el) return;
      const tag = el.tagName ? el.tagName.toLowerCase() : '';
      if (tag !== 'textarea') {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
    }
  }, true);
})();
</script>
""", unsafe_allow_html=True)


def get_client():
    api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY not set.")
        st.stop()

    genai.configure(api_key=api_key)
    return genai



def generate_diet_plan(prompt: str):
    client = get_client()
    response = client.GenerativeModel("gemini-2.5-flash").generate_content(prompt)
    return response.text


def build_prompt(goal, age, height, weight, gender, diet_pref, activity, notes):
    template = """
Generate a personalized, budget-friendly Indian diet plan with:

1. Summary of health condition & goal
2. Daily calorie requirement
3. Full-day diet chart:
   - Early Morning
   - Breakfast
   - Mid-Morning Snack
   - Lunch
   - Evening Snack
   - Dinner
4. 7-day rotation diet table
5. Water intake & 8 lifestyle tips

User Details:
Goal: {goal}
Age: {age}
Height: {height}
Weight: {weight}
Gender: {gender}
Diet Preference: {diet_pref}
Activity Level: {activity}
Special Notes: {notes}

Important:
- Follow dietary preference strictly.
- Keep meals budget-friendly & Indian.
- Use clear headings and bullet points.
"""
    return template.format(
        goal=goal,
        age=age,
        height=height,
        weight=weight,
        gender=gender,
        diet_pref=diet_pref,
        activity=activity,
        notes=notes if notes.strip() else "None"
    )


def main():

    st.markdown("<h1 style='text-align:center;color:#00aa77;'>🥗 Smart Diet Planner</h1>",
                unsafe_allow_html=True)

    with st.form("diet_form"):
        col1, col2 = st.columns(2)

        with col1:
            goal = st.selectbox("Goal", ["Lose weight", "Maintain weight", "Gain weight"])
            age = st.number_input("Age (Years)", min_value=10, max_value=100, value=21)

        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            diet_pref = st.selectbox("Diet Preference", ["Veg", "Non-Veg", "Both"])

        col3, col4 = st.columns(2)

        with col3:
            height = st.text_input("Height (e.g., 170 cm)", value="170 cm")

        with col4:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=250.0, value=70.0)

        activity = st.selectbox(
            "Daily Activity",
            ["Not active at all", "Partially active", "Very active"]
        )

        notes = st.text_area(
            "Additional Notes (optional)",
            placeholder="Eg: lactose intolerant, avoid spicy food, hostel mess only...",
            height=120
        )

        submit = st.form_submit_button("Generate Diet Plan ✨")

    if submit:
        prompt = build_prompt(goal, age, height, weight, gender, diet_pref, activity, notes)

        with st.spinner("Creating your personalized diet plan..."):
            diet_plan = generate_diet_plan(prompt)

        st.success("Diet Plan Ready!")

        st.markdown("## 📄 Your Diet Plan")
        st.markdown(diet_plan)

        st.markdown(
            """
            <div style="
                margin-top:18px;
                padding:18px;
                border-radius:12px;
                background: linear-gradient(90deg, #eafff3, #f0fff8);
                box-shadow: 0 6px 18px rgba(0,0,0,0.06);
                text-align:center;
                font-size:16px;
                color:#006644;
                ">
                <div style="font-size:22px; margin-bottom:6px;">🙏 Thank you for using our service</div>
                <div style="font-weight:600;">Visit Again — we'd love to help you stay healthy!</div>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
