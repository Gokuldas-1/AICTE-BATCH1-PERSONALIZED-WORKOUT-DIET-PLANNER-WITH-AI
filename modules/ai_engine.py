"""
Google Gemini AI Engine
Handles all AI-powered plan generation and chat functionality.
"""
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4096
    )

    return response.choices[0].message.content
# ─────────────────────────────────────────────
# Workout Plan Generator
# ─────────────────────────────────────────────

def generate_workout_plan(profile: dict) -> str:
    """
    Generate a personalized weekly workout plan using Gemini.
    Returns the plan as a formatted markdown string.
    """

    prompt = f"""
You are an expert certified personal trainer and fitness coach. Generate a highly personalized, 
practical, and motivating 7-day weekly workout plan for a student with the following profile:

**Student Profile:**
- Name: {profile.get('name', 'Student')}
- Age: {profile.get('age')} years old
- Gender: {profile.get('gender')}
- Height: {profile.get('height_cm')} cm | Weight: {profile.get('weight_kg')} kg
- Fitness Goal: {profile.get('goal')}
- Current Fitness Level: {profile.get('fitness_level')}
- Available Equipment: {profile.get('equipment')}
- Activity Level: {profile.get('activity_level')}
- Budget Constraint: Student on tight budget (₹{profile.get('budget_inr', 200)}/day for food)

**Important Guidelines:**
1. Design workouts appropriate for a {profile.get('fitness_level', 'Beginner')} level
2. Only use exercises possible with: {profile.get('equipment')}
3. Keep sessions under 45-60 minutes (student schedule)
4. Include warm-up and cool-down
5. Include at least 1-2 rest/active recovery days
6. For each exercise, specify: sets × reps (or duration), form tip, and estimated calories burned
7. Include motivational notes for each day

Format the response as structured markdown with:
- Day headers (## Monday, ## Tuesday, etc.)
- Session type (e.g., **Upper Body Strength**, **Cardio & Core**)
- Exercise table with columns: Exercise | Sets × Reps | Rest | Tip
- Daily summary with estimated total calories burned
- Weekly overview at the end

Make it practical, science-backed, and genuinely helpful for a busy student.
"""

    return ask_ai(prompt)

# ─────────────────────────────────────────────
# Diet / Meal Plan Generator
# ─────────────────────────────────────────────

def generate_diet_plan(profile: dict, macro_targets: dict) -> str:
    """
    Generate a personalized 7-day culturally-appropriate meal plan.
    """

    prompt = f"""
You are a registered dietitian nutritionist specializing in student nutrition and Indian/global cuisines.
Create a comprehensive, practical, and delicious 7-day meal plan for a student.

**Student Profile:**
- Name: {profile.get('name', 'Student')}
- Age: {profile.get('age')} | Gender: {profile.get('gender')}
- Weight: {profile.get('weight_kg')} kg | Goal: {profile.get('goal')}
- Dietary Preference: {profile.get('dietary_pref')}
- Cultural Background / Cuisine Preference: {profile.get('cultural_bg')}
- Daily Budget: ₹{profile.get('budget_inr', 200)} per day for all meals
- Allergies/Restrictions: {profile.get('allergies', 'None')}

**Daily Nutrition Targets:**
- Calories: {macro_targets.get('calories')} kcal
- Protein: {macro_targets.get('protein_g')}g
- Carbohydrates: {macro_targets.get('carbs_g')}g  
- Fat: {macro_targets.get('fat_g')}g

**Critical Requirements:**
1. STRICTLY respect the dietary preference: {profile.get('dietary_pref')}
2. Use culturally familiar foods from {profile.get('cultural_bg')} cuisine
3. ALL meals must be within the ₹{profile.get('budget_inr', 200)}/day budget
4. Use easily available, affordable ingredients (no exotic imports)
5. Include simple recipes students can cook in a hostel/PG (minimal equipment)
6. Provide approximate cost per meal in ₹
7. Include macro breakdown per day
8. Add practical meal prep tips to save time and money

**Format for each day:**
## [Day Name]
**Budget: ₹XX | Calories: XXXX kcal | Protein: XXg | Carbs: XXg | Fat: XXg**

### 🌅 Breakfast (~₹XX)
- Food items with quantity
- Simple prep instructions (2-3 lines max)

### ☀️ Mid-Morning Snack (~₹XX)
- Food items

### 🍽️ Lunch (~₹XX)
- Food items with quantity
- Simple prep instructions

### 🍎 Evening Snack (~₹XX)
- Food items

### 🌙 Dinner (~₹XX)
- Food items with quantity
- Simple prep instructions

---

Include a **Weekly Shopping List** at the end with approximate costs.
Make meals varied, nutritious, and genuinely enjoyable — not boring diet food!
"""

    return ask_ai(prompt)


# ─────────────────────────────────────────────
# Recipe Suggestion
# ─────────────────────────────────────────────

def get_recipe_suggestion(meal_name: str, dietary_pref: str, budget: float = 50) -> str:
    """Get a quick AI recipe for a specific meal."""

    prompt = f"""
Give me a simple, budget-friendly recipe for: **{meal_name}**
- Dietary: {dietary_pref}
- Budget: ₹{budget} max
- For a student with basic cooking skills and minimal equipment

Format:
**Ingredients** (with quantities and approx. cost)
**Steps** (numbered, clear, under 5-7 steps)
**Nutrition per serving:** Calories | Protein | Carbs | Fat
**Time:** Prep + Cook time
**Storage tip:** (if applicable)
"""

    return ask_ai(prompt)


# ─────────────────────────────────────────────
# AI Fitness Coach Chat
# ─────────────────────────────────────────────

def chat_with_coach(user_message: str, profile: dict, chat_history: list) -> str:
    """
    AI fitness coach with memory of conversation.
    """

    system_context = f"""You are FitBot, an expert AI fitness and nutrition coach.
You are friendly, encouraging, and science-backed. You are helping a student named {profile.get('name', 'there')}.

Student profile: {profile.get('age')}yo {profile.get('gender')}, Goal: {profile.get('goal')},
Diet: {profile.get('dietary_pref')}, Culture: {profile.get('cultural_bg')},
Budget: ₹{profile.get('budget_inr', 200)}/day, Equipment: {profile.get('equipment')}.

Keep responses concise, practical, and motivating. Use emojis sparingly."""

    full_message = f"""
{system_context}

Student Question:
{user_message}
"""

    return ask_ai(full_message)


# ─────────────────────────────────────────────
# Progress Analysis
# ─────────────────────────────────────────────

def analyze_progress(profile: dict, weight_history: list, weekly_summary: dict) -> str:
    """Generate AI progress analysis and recommendations."""

    weight_trend = "no data"

    if len(weight_history) >= 2:
        diff = weight_history[-1]["weight_kg"] - weight_history[0]["weight_kg"]
        weight_trend = f"{'+' if diff > 0 else ''}{diff:.1f} kg over {len(weight_history)} days"

    prompt = f"""
Analyze this student's fitness progress and provide personalized recommendations.

Profile:
- Goal: {profile.get('goal')}
- Starting Weight: {profile.get('weight_kg')} kg

Weight Trend:
{weight_trend}

This Week's Stats:
- Calories consumed: {weekly_summary.get('calories_consumed', 0):.0f} kcal
- Protein: {weekly_summary.get('protein', 0):.0f} g
- Workout time: {weekly_summary.get('workout_minutes', 0)} minutes
- Calories burned: {weekly_summary.get('calories_burned', 0):.0f} kcal

Give:
1. Progress Assessment (2-3 sentences)
2. What's Working (2 bullet points)
3. Areas to Improve (2-3 actionable tips)
4. Motivational Message (1-2 sentences)

Keep it encouraging and specific.
"""

    return ask_ai(prompt)