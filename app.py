"""
FitAI Planner - Main Streamlit Application
Personalized Workout & Diet Planner powered by Google Gemini AI
"""

import os
import json
import datetime
import importlib
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

# ─── Page Config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="FitAI Planner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "FitAI Planner – AI-powered personalized fitness & diet planning"}
)

# ─── Load env & modules ──────────────────────────────────────────────────────
load_dotenv()

from config.settings import (
    APP_NAME, FITNESS_GOALS, DIETARY_PREFERENCES, CULTURAL_BACKGROUNDS,
    EQUIPMENT_OPTIONS, FITNESS_LEVELS, ACTIVITY_MULTIPLIERS, DAYS_OF_WEEK
)
from database import db_manager as _db_manager

db_manager = importlib.reload(_db_manager)

init_db = db_manager.init_db
save_profile = db_manager.save_profile
load_profile = db_manager.load_profile
save_plan = db_manager.save_plan
load_plan = db_manager.load_plan
log_meal = db_manager.log_meal
get_meals_for_date = db_manager.get_meals_for_date
delete_meal_log = db_manager.delete_meal_log
log_workout = db_manager.log_workout
get_workouts_for_date = db_manager.get_workouts_for_date
delete_workout_log = db_manager.delete_workout_log
log_weight = db_manager.log_weight
get_weight_history = db_manager.get_weight_history
get_streak = db_manager.get_streak
get_weekly_summary = db_manager.get_weekly_summary
register_user = db_manager.register_user
get_user_by_email = db_manager.get_user_by_email
get_user_by_id = db_manager.get_user_by_id
save_api_key = db_manager.save_api_key
get_api_key = db_manager.get_api_key
from modules.bmi_calculator import (
    calculate_bmi, get_bmi_category, calculate_bmr, calculate_tdee,
    get_macro_targets, get_ideal_weight_range, get_water_intake
)
from modules.ai_engine import (
    generate_workout_plan,
    generate_diet_plan,
    get_recipe_suggestion,
    chat_with_coach,
    analyze_progress
)
from modules.auth import (
    hash_password, verify_password, encrypt_api_key, decrypt_api_key,
    is_valid_email, is_valid_password
)

# ─── Initialize DB ──────────────────────────────────────────────────────────
init_db()

# ─── Load CSS ────────────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Load Food DB ─────────────────────────────────────────────────────────────
food_db_path = os.path.join(os.path.dirname(__file__), "data", "food_database.json")
with open(food_db_path) as f:
    FOOD_DB = json.load(f)

# ─── Session State ────────────────────────────────────────────────────────────
# User Authentication
if "user" not in st.session_state:
    st.session_state.user = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_profile():
    return load_profile()


def check_api_key():
    """Load and validate API key for current user."""
    if not st.session_state.user:
        st.warning("Please log in first to use AI features.")
        return False
    
    # Load encrypted API key from database
    if not st.session_state.api_key:
        encrypted_key = get_api_key(st.session_state.user["id"])
        if encrypted_key:
            st.session_state.api_key = decrypt_api_key(encrypted_key)
    
    if not st.session_state.api_key:
        st.warning("No API key configured. Please add it during registration or update your stored profile.")
        return False
    
    try:
      return True
    except Exception as e:
      st.error(f"Invalid API key: {e}")
    return False


def render_macro_bar(label: str, value: float, target: float, color_class: str):
    pct = min(int((value / target) * 100), 100) if target > 0 else 0
    st.markdown(f"""
    <div style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px">
        <span style="color:#94A3B8;font-size:0.8rem;font-weight:500">{label}</span>
        <span style="color:#E2E8F0;font-size:0.8rem;font-weight:600">{value:.0f}g / {target}g</span>
      </div>
      <div class="macro-bar">
        <div class="macro-fill-{color_class}" style="width:{pct}%;height:100%;border-radius:50px;transition:width 0.8s ease"></div>
      </div>
      <div style="text-align:right;font-size:0.7rem;color:#64748B;margin-top:2px">{pct}%</div>
    </div>
    """, unsafe_allow_html=True)


def bmi_gauge(bmi: float, category: str) -> go.Figure:
    cat_colors = {"Underweight": "#FFC75F", "Normal Weight": "#00C9A7", "Overweight": "#FF6B6B", "Obese": "#FF3232"}
    color = cat_colors.get(category, "#00C9A7")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmi,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": category, "font": {"size": 16, "color": color}},
        gauge={
            "axis": {"range": [10, 40], "tickwidth": 1, "tickcolor": "#64748B", "tickfont": {"color": "#94A3B8"}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#111827",
            "borderwidth": 2,
            "bordercolor": "#1A2332",
            "steps": [
                {"range": [10, 18.5], "color": "rgba(255,199,95,0.15)"},
                {"range": [18.5, 25], "color": "rgba(0,201,167,0.15)"},
                {"range": [25, 30], "color": "rgba(255,107,107,0.15)"},
                {"range": [30, 40], "color": "rgba(255,50,50,0.2)"},
            ],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.75, "value": bmi},
        },
        number={"font": {"size": 32, "color": color}, "suffix": ""},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0"},
        height=250,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
    )
    return fig


def macro_pie(macros: dict) -> go.Figure:
    labels = ["Protein", "Carbs", "Fat"]
    values = [macros["protein_g"], macros["carbs_g"], macros["fat_g"]]
    colors_list = ["#00C9A7", "#845EC2", "#FF6B6B"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker={"colors": colors_list, "line": {"color": "#0A0E1A", "width": 2}},
        textfont={"color": "#E2E8F0", "size": 12},
        hovertemplate="<b>%{label}</b><br>%{value}g (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{macros['calories']}</b><br><span style='font-size:10px'>kcal/day</span>",
        x=0.5, y=0.5, showarrow=False,
        font={"size": 18, "color": "#00C9A7"}
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "#94A3B8"}, "bgcolor": "rgba(0,0,0,0)"},
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
        height=260,
        showlegend=True,
    )
    return fig


def weight_chart(history: list) -> go.Figure:
    if not history:
        return None
    df = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["log_date"], y=df["weight_kg"],
        mode="lines+markers",
        line={"color": "#00C9A7", "width": 2.5, "shape": "spline"},
        marker={"color": "#00C9A7", "size": 8, "line": {"color": "#0A0E1A", "width": 2}},
        fill="tozeroy",
        fillcolor="rgba(0,201,167,0.08)",
        name="Weight",
        hovertemplate="<b>%{x}</b><br>%{y} kg<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"gridcolor": "rgba(255,255,255,0.05)", "color": "#64748B", "tickfont": {"color": "#94A3B8"}},
        yaxis={"gridcolor": "rgba(255,255,255,0.05)", "color": "#64748B", "tickfont": {"color": "#94A3B8"}},
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        height=250,
        showlegend=False,
    )
    return fig


def daily_cal_chart(meals: list, target: int) -> go.Figure:
    if not meals:
        return None

    meal_types = ["Breakfast", "Mid-Morning Snack", "Lunch", "Evening Snack", "Dinner"]
    cal_by_type = {}
    for m in meals:
        mt = m["meal_type"]
        cal_by_type[mt] = cal_by_type.get(mt, 0) + m["calories"]

    labels = [mt for mt in meal_types if mt in cal_by_type]
    vals = [cal_by_type[mt] for mt in labels]
    colors_map = ["#00C9A7", "#845EC2", "#FF6B6B", "#FFC75F", "#4FC3F7"]

    fig = go.Figure(go.Bar(
        x=labels, y=vals,
        marker={"color": colors_map[:len(labels)], "opacity": 0.85,
                "line": {"color": "#0A0E1A", "width": 1}},
        text=[f"{v:.0f}" for v in vals],
        textposition="outside",
        textfont={"color": "#E2E8F0"},
        hovertemplate="<b>%{x}</b><br>%{y:.0f} kcal<extra></extra>",
    ))
    fig.add_hline(y=target, line_dash="dash", line_color="#FF6B6B",
                  annotation_text=f"Target: {target} kcal",
                  annotation_font_color="#FF6B6B")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"gridcolor": "rgba(255,255,255,0.05)", "color": "#64748B", "tickfont": {"color": "#94A3B8"}},
        yaxis={"gridcolor": "rgba(255,255,255,0.05)", "color": "#64748B", "tickfont": {"color": "#94A3B8"}},
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        height=250,
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION - LOGIN & REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

if not st.session_state.user:
    # Show login/register page
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="hero-banner" style="text-align:center;padding:40px 20px">
          <div style="font-size:3.5rem;margin-bottom:12px">💪</div>
          <h1 style="color:#00C9A7;font-size:2.5rem;font-weight:800;margin:0 0 8px">FitAI Planner</h1>
          <p style="color:#94A3B8;font-size:1rem;margin:0">Your AI-powered personal fitness coach</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            st.markdown("### Login to Your Account")
            email = st.text_input("Email", placeholder="student@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter both email and password")
                elif not is_valid_email(email):
                    st.error("Invalid email format")
                else:
                    user = get_user_by_email(email)
                    if user and verify_password(password, user["password_hash"]):
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
        
        with auth_tab2:
            st.markdown("### Create New Account")
            reg_email = st.text_input("Email", placeholder="student@example.com", key="reg_email")
            reg_name = st.text_input("Full Name", placeholder="Your Name", key="reg_name")
            reg_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
            reg_api_key = st.text_input(
                "Groq API Key (optional)",
                type="password",
                placeholder="Paste your Gemini key here to enable AI features",
                key="reg_api_key"
            )
            
            if st.button("Register", use_container_width=True, type="primary"):
                if not all([reg_email, reg_name, reg_password]):
                    st.error("Please fill all fields")
                elif not is_valid_email(reg_email):
                    st.error("Invalid email format")
                elif not is_valid_password(reg_password):
                    st.error("Password must be at least 6 characters")
                elif reg_password != reg_password_confirm:
                    st.error("Passwords don't match")
                elif get_user_by_email(reg_email):
                    st.error("Email already registered")
                else:
                    password_hash = hash_password(reg_password)
                    user = register_user(reg_email, password_hash, reg_name)
                    if user:
                        if reg_api_key:
                            encrypted_key = encrypt_api_key(reg_api_key)
                            save_api_key(user["id"], encrypted_key)
                            st.session_state.api_key = reg_api_key
                        st.session_state.user = user
                        st.success("Account created! Logging you in...")
                        st.rerun()
                    else:
                        st.error("Registration failed. Try again.")
    
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px">
      <div style="font-size:3rem;margin-bottom:4px">💪</div>
      <div style="font-size:1.4rem;font-weight:800;color:#00C9A7;letter-spacing:-0.02em">FitAI Planner</div>
      <div style="font-size:0.75rem;color:#64748B;margin-top:2px">Powered by Groq Llama 3.3</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # User Profile & Settings
    if st.session_state.user:
        st.markdown(f"<div style='color:#00C9A7;font-weight:600'>User: {st.session_state.user.get('full_name', st.session_state.user['email'])}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Settings", use_container_width=True):
                st.session_state.page = "Settings"
                st.rerun()
        with col2:
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.api_key = None
                st.session_state.chat_history = []
                st.session_state.page = "Dashboard"
                st.rerun()
        
        st.markdown("---")

    # Navigation
    st.markdown("<div style='color:#64748B;font-size:0.75rem;font-weight:600;letter-spacing:0.08em;margin-bottom:8px'>NAVIGATION</div>", unsafe_allow_html=True)

    pages = [
        ("🏠 Dashboard", "Dashboard"),
        ("👤 My Profile", "Profile"),
        ("💪 Workout Plan", "Workout"),
        ("🥗 Diet Plan", "Diet"),
        ("📓 Log Today", "Log"),
        ("📊 Progress", "Progress"),
        ("🤖 AI Coach", "Coach"),
        ("📄 Export PDF", "Export"),
    ]

    for icon_label, key in pages:
        is_active = st.session_state.page == icon_label
        if st.button(
            icon_label,
            use_container_width=True,
            type="primary" if is_active else "secondary",
            key=f"nav_{key}"
        ):
            st.session_state.page = icon_label
            st.rerun()

    st.markdown("---")

    # Quick stats in sidebar
    profile = get_profile()
    if profile:
        bmi = calculate_bmi(profile["weight_kg"], profile["height_cm"])
        cat, _ = get_bmi_category(bmi)
        streak = get_streak()
        st.markdown(f"""
        <div style="background:rgba(0,201,167,0.05);border:1px solid rgba(0,201,167,0.2);border-radius:12px;padding:14px">
          <div style="font-size:0.7rem;color:#64748B;font-weight:600;letter-spacing:0.08em;margin-bottom:8px">QUICK STATS</div>
          <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:#94A3B8;font-size:0.8rem">BMI</span>
            <span style="color:#00C9A7;font-weight:700">{bmi}</span>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:#94A3B8;font-size:0.8rem">Goal</span>
            <span style="color:#E2E8F0;font-weight:600;font-size:0.8rem">{profile.get('goal','—')}</span>
          </div>
          <div style="display:flex;justify-content:space-between">
            <span style="color:#94A3B8;font-size:0.8rem">🔥 Streak</span>
            <span style="color:#FFC75F;font-weight:700">{streak} days</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "🏠 Dashboard":
    profile = get_profile()

    if not profile:
        st.markdown("""
        <div class="hero-banner">
          <div style="font-size:3.5rem;margin-bottom:12px">💪</div>
          <h1 style="color:#00C9A7;font-size:2.5rem;font-weight:800;margin:0 0 8px">Welcome to FitAI Planner</h1>
          <p style="color:#94A3B8;font-size:1.1rem;margin:0 0 24px">Your AI-powered personalized fitness & nutrition companion</p>
          <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
            <div style="background:rgba(0,201,167,0.1);border:1px solid rgba(0,201,167,0.3);border-radius:12px;padding:12px 20px;color:#E2E8F0">🎯 Personalized Plans</div>
            <div style="background:rgba(132,94,194,0.1);border:1px solid rgba(132,94,194,0.3);border-radius:12px;padding:12px 20px;color:#E2E8F0">🥗 Cultural Meal Plans</div>
            <div style="background:rgba(255,107,107,0.1);border:1px solid rgba(255,107,107,0.3);border-radius:12px;padding:12px 20px;color:#E2E8F0">💰 Budget Friendly</div>
            <div style="background:rgba(255,199,95,0.1);border:1px solid rgba(255,199,95,0.3);border-radius:12px;padding:12px 20px;color:#E2E8F0">📊 Progress Tracking</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.info("👆 **Get Started**: Click **👤 My Profile** in the sidebar to create your personalized profile and begin your fitness journey!")
        st.stop()

    # ── Header ──
    streak = get_streak()
    today = datetime.date.today().strftime("%A, %d %B %Y")

    bmi = calculate_bmi(profile["weight_kg"], profile["height_cm"])
    cat, emoji = get_bmi_category(bmi)
    bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
    tdee = calculate_tdee(bmr, profile["activity_level"])
    macros = get_macro_targets(tdee, profile["goal"])
    water = get_water_intake(profile["weight_kg"], profile["activity_level"])

    st.markdown(f"""
    <div class="hero-banner">
      <div style="font-size:0.85rem;color:#64748B;margin-bottom:4px">{today}</div>
      <h1 style="color:#E2E8F0;font-size:2rem;font-weight:800;margin:0 0 4px">
        Hey, {profile.get('name', 'Champ')}! <span style="color:#FFC75F">🔥</span>
      </h1>
      <p style="color:#94A3B8;margin:0 0 16px">Goal: <strong style="color:#00C9A7">{profile.get('goal')}</strong> | {streak} day streak</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Top Metrics ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("BMI", bmi, delta=None, help="Body Mass Index")
        st.caption(f"**{cat}** {emoji}")
    with c2:
        st.metric("Daily Calories", f"{macros['calories']} kcal", help="Your calorie target based on goal")
    with c3:
        st.metric("🔥 Workout Streak", f"{streak} days", help="Consecutive days you've logged a workout")
    with c4:
        st.metric("💧 Water Goal", f"{water} L/day", help="Recommended daily water intake")
    with c5:
        ideal_min, ideal_max = get_ideal_weight_range(profile["height_cm"])
        st.metric("Ideal Weight", f"{ideal_min}–{ideal_max} kg", help="Healthy weight range for your height")

    st.markdown("---")

    # ── BMI + Macros ──
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📊 BMI Analysis")
        st.plotly_chart(bmi_gauge(bmi, cat), use_container_width=True, config={"displayModeBar": False})
        badge_class = {"Normal Weight": "normal", "Underweight": "underweight",
                       "Overweight": "overweight", "Obese": "obese"}.get(cat, "normal")
        st.markdown(f"""
        <div style="text-align:center;margin-top:-10px">
          <span class="bmi-badge badge-{badge_class}">{cat}</span>
          <div style="color:#64748B;font-size:0.8rem;margin-top:8px">
            Ideal range: {ideal_min}–{ideal_max} kg
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 🎯 Daily Macro Targets")
        st.plotly_chart(macro_pie(macros), use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── Today's Summary ──
    today_str = str(datetime.date.today())
    today_meals = get_meals_for_date(today_str)
    today_workouts = get_workouts_for_date(today_str)

    total_cal_today = sum(m["calories"] for m in today_meals)
    total_protein = sum(m["protein"] for m in today_meals)
    total_carbs = sum(m["carbs"] for m in today_meals)
    total_fat = sum(m["fat"] for m in today_meals)
    cal_burned = sum(w["calories_burned"] for w in today_workouts)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🍽️ Today's Nutrition")
        cal_pct = int((total_cal_today / macros["calories"]) * 100) if macros["calories"] else 0

        st.markdown(f"""
        <div class="glass-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <span style="color:#94A3B8">Calories Consumed</span>
            <span style="color:#00C9A7;font-size:1.4rem;font-weight:700">{total_cal_today:.0f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(min(cal_pct / 100, 1.0))
        st.caption(f"{cal_pct}% of daily target ({macros['calories']} kcal)")

        render_macro_bar("🟢 Protein", total_protein, macros["protein_g"], "protein")
        render_macro_bar("🟣 Carbs", total_carbs, macros["carbs_g"], "carbs")
        render_macro_bar("🔴 Fat", total_fat, macros["fat_g"], "fat")

        if today_meals:
            chart = daily_cal_chart(today_meals, macros["calories"])
            if chart:
                st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown("#### 💪 Today's Workout")

        if today_workouts:
            total_min = sum(w.get("duration_min", 0) for w in today_workouts)
            st.markdown(f"""
            <div class="glass-card">
              <div style="display:flex;gap:24px;margin-bottom:12px">
                <div>
                  <div style="color:#64748B;font-size:0.75rem">Calories Burned</div>
                  <div style="color:#FF6B6B;font-size:1.6rem;font-weight:700">{cal_burned:.0f}</div>
                </div>
                <div>
                  <div style="color:#64748B;font-size:0.75rem">Time</div>
                  <div style="color:#FFC75F;font-size:1.6rem;font-weight:700">{total_min} min</div>
                </div>
                <div>
                  <div style="color:#64748B;font-size:0.75rem">Exercises</div>
                  <div style="color:#845EC2;font-size:1.6rem;font-weight:700">{len(today_workouts)}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            for w in today_workouts:
                st.markdown(f"""
                <div style="background:rgba(132,94,194,0.08);border:1px solid rgba(132,94,194,0.2);
                     border-radius:10px;padding:10px 14px;margin-bottom:6px;display:flex;justify-content:space-between">
                  <span style="color:#E2E8F0;font-weight:500">💪 {w['exercise_name']}</span>
                  <span style="color:#64748B;font-size:0.85rem">{w.get('sets',0)}×{w.get('reps',0)} | {w.get('duration_min',0)}min</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:32px">
              <div style="font-size:2.5rem;margin-bottom:8px">🏃</div>
              <div style="color:#94A3B8">No workout logged today</div>
              <div style="color:#64748B;font-size:0.85rem;margin-top:4px">Go log your workout!</div>
            </div>
            """, unsafe_allow_html=True)

        # Net calories
        net_cal = total_cal_today - cal_burned
        remaining = macros["calories"] - net_cal
        st.markdown(f"""
        <div style="background:rgba(0,201,167,0.05);border:1px solid rgba(0,201,167,0.2);border-radius:12px;padding:16px;margin-top:12px">
          <div style="color:#94A3B8;font-size:0.8rem;margin-bottom:4px">Remaining Calories</div>
          <div style="color:#00C9A7;font-size:2rem;font-weight:800">{remaining:.0f} kcal</div>
          <div style="color:#64748B;font-size:0.75rem">Target {macros['calories']} − Consumed {total_cal_today:.0f} + Burned {cal_burned:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Quick Action Buttons ──
    st.markdown("---")
    st.markdown("#### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("💪 Generate Workout Plan", use_container_width=True):
            st.session_state.page = "💪 Workout Plan"
            st.rerun()
    with qa2:
        if st.button("🥗 Generate Diet Plan", use_container_width=True):
            st.session_state.page = "🥗 Diet Plan"
            st.rerun()
    with qa3:
        if st.button("📓 Log Today's Meals", use_container_width=True):
            st.session_state.page = "📓 Log Today"
            st.rerun()
    with qa4:
        if st.button("🤖 Chat with AI Coach", use_container_width=True):
            st.session_state.page = "🤖 AI Coach"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "👤 My Profile":
    st.markdown("## 👤 My Profile")
    st.markdown("<p style='color:#94A3B8'>Complete your profile to get a personalized AI-generated plan.</p>", unsafe_allow_html=True)

    existing = get_profile() or {}

    with st.form("profile_form"):
        st.markdown("### 🧍 Personal Information")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", value=existing.get("name", ""), placeholder="e.g., Arjun Sharma")
            age = st.number_input("Age *", min_value=10, max_value=80, value=int(existing.get("age", 20)))
            height_cm = st.number_input("Height (cm) *", min_value=100.0, max_value=250.0,
                                        value=float(existing.get("height_cm", 170.0)), step=0.5)
        with c2:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"],
                                  index=["Male", "Female", "Other"].index(existing.get("gender", "Male")))
            weight_kg = st.number_input("Current Weight (kg) *", min_value=20.0, max_value=300.0,
                                        value=float(existing.get("weight_kg", 65.0)), step=0.5)
            budget_inr = st.number_input("Daily Food Budget (₹) *", min_value=50, max_value=2000,
                                         value=int(existing.get("budget_inr", 200)), step=10,
                                         help="Your daily budget for all meals")

        st.markdown("### 🎯 Fitness Profile")
        c3, c4 = st.columns(2)
        with c3:
            goal = st.selectbox("Primary Fitness Goal *", FITNESS_GOALS,
                                index=FITNESS_GOALS.index(existing.get("goal", FITNESS_GOALS[0])))
            fitness_level = st.selectbox("Current Fitness Level *", FITNESS_LEVELS,
                                         index=FITNESS_LEVELS.index(existing.get("fitness_level", FITNESS_LEVELS[0])))
            equipment = st.selectbox("Available Equipment *", EQUIPMENT_OPTIONS,
                                     index=EQUIPMENT_OPTIONS.index(existing.get("equipment", EQUIPMENT_OPTIONS[0])))
        with c4:
            activity_level = st.selectbox("Activity Level *", list(ACTIVITY_MULTIPLIERS.keys()),
                                          index=list(ACTIVITY_MULTIPLIERS.keys()).index(
                                              existing.get("activity_level", list(ACTIVITY_MULTIPLIERS.keys())[0])))
            dietary_pref = st.selectbox("Dietary Preference *", DIETARY_PREFERENCES,
                                        index=DIETARY_PREFERENCES.index(existing.get("dietary_pref", DIETARY_PREFERENCES[0])))
            cultural_bg = st.selectbox("Cultural / Cuisine Background *", CULTURAL_BACKGROUNDS,
                                       index=CULTURAL_BACKGROUNDS.index(existing.get("cultural_bg", CULTURAL_BACKGROUNDS[0])))

        allergies = st.text_area("Food Allergies / Medical Restrictions",
                                 value=existing.get("allergies", ""),
                                 placeholder="e.g., lactose intolerant, nut allergy, diabetes...",
                                 height=80)

        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

        if submitted:
            if not name:
                st.error("Please enter your name.")
            else:
                profile_data = {
                    "name": name, "age": age, "gender": gender,
                    "height_cm": height_cm, "weight_kg": weight_kg,
                    "goal": goal, "dietary_pref": dietary_pref,
                    "cultural_bg": cultural_bg, "activity_level": activity_level,
                    "equipment": equipment, "fitness_level": fitness_level,
                    "budget_inr": budget_inr, "allergies": allergies,
                }
                save_profile(profile_data)
                # Auto-log weight
                log_weight(str(datetime.date.today()), weight_kg)
                st.success("✅ Profile saved successfully! Your AI plans will now be personalized.")
                st.balloons()

    # Show computed metrics if profile exists
    profile = get_profile()
    if profile:
        st.markdown("---")
        st.markdown("### 📊 Your Health Metrics")
        bmi = calculate_bmi(profile["weight_kg"], profile["height_cm"])
        cat, emoji = get_bmi_category(bmi)
        bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
        tdee = calculate_tdee(bmr, profile["activity_level"])
        macros = get_macro_targets(tdee, profile["goal"])
        water = get_water_intake(profile["weight_kg"], profile["activity_level"])

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("BMI", f"{bmi} ({cat} {emoji})")
        m2.metric("BMR", f"{bmr:.0f} kcal/day", help="Basal Metabolic Rate")
        m3.metric("TDEE", f"{tdee} kcal/day", help="Total Daily Energy Expenditure")
        m4.metric("Daily Target", f"{macros['calories']} kcal")
        m5.metric("Water Intake", f"{water} L/day")

        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(bmi_gauge(bmi, cat), use_container_width=True, config={"displayModeBar": False})
        with col_right:
            st.plotly_chart(macro_pie(macros), use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: WORKOUT PLAN
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "💪 Workout Plan":
    st.markdown("## 💪 Your Personalized Workout Plan")

    profile = get_profile()
    if not profile:
        st.warning("Please complete your profile first!")
        st.stop()

    # Show existing plan or generate new
    existing_plan = load_plan("workout")

    col_gen, col_info = st.columns([2, 3])
    with col_gen:
        st.markdown(f"""
        <div class="glass-card">
          <div style="color:#64748B;font-size:0.8rem;margin-bottom:8px">PROFILE SUMMARY</div>
          <div style="color:#E2E8F0"><b>Goal:</b> {profile.get('goal')}</div>
          <div style="color:#E2E8F0"><b>Level:</b> {profile.get('fitness_level')}</div>
          <div style="color:#E2E8F0"><b>Equipment:</b> {profile.get('equipment')}</div>
          <div style="color:#E2E8F0"><b>Duration:</b> 45-60 min/session</div>
        </div>
        """, unsafe_allow_html=True)

        generate_btn = st.button("🤖 Generate AI Workout Plan", use_container_width=True, type="primary")
        if existing_plan:
            st.caption("✅ Plan generated — click to regenerate")

    with col_info:
        if not existing_plan:
            st.info("Click **Generate AI Workout Plan** to create your personalized 7-day workout routine using Google Gemini AI.")

    if generate_btn:
        if not check_api_key():
            st.stop()
        with st.spinner("🤖 AI is crafting your personalized workout plan..."):
            try:
                plan = generate_workout_plan(profile)
                save_plan("workout", plan)
                st.success("✅ Your 7-day workout plan has been generated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating plan: {e}")

    if existing_plan:
        st.markdown("---")
        # Parse and display day by day
        days_content = {}
        current_day = None
        current_content = []

        for line in existing_plan.split("\n"):
            if line.strip().startswith("## "):
                if current_day and current_content:
                    days_content[current_day] = "\n".join(current_content)
                current_day = line.strip()[3:]
                current_content = []
            elif current_day:
                current_content.append(line)

        if current_day and current_content:
            days_content[current_day] = "\n".join(current_content)

        if days_content:
            selected_day = st.selectbox("📅 View Day", list(days_content.keys()))
            if selected_day and selected_day in days_content:
                st.markdown(f"""
                <div class="day-card">
                  <h3 style="color:#845EC2;margin:0 0 12px">📅 {selected_day}</h3>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(days_content[selected_day])
        else:
            st.markdown(existing_plan)

        with st.expander("📄 View Full Plan (Raw)"):
            st.markdown(existing_plan)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DIET PLAN
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "🥗 Diet Plan":
    st.markdown("## 🥗 Your Personalized Diet Plan")

    profile = get_profile()
    if not profile:
        st.warning("Please complete your profile first!")
        st.stop()

    bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
    tdee = calculate_tdee(bmr, profile["activity_level"])
    macros = get_macro_targets(tdee, profile["goal"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 Daily Calories", f"{macros['calories']} kcal")
    col2.metric("🥩 Protein", f"{macros['protein_g']}g")
    col3.metric("🍚 Carbs", f"{macros['carbs_g']}g")
    col4.metric("🫒 Fat", f"{macros['fat_g']}g")

    existing_diet = load_plan("diet")

    gen_col, info_col = st.columns([1, 2])
    with gen_col:
        st.markdown(f"""
        <div class="glass-card">
          <div style="color:#64748B;font-size:0.8rem;margin-bottom:8px">DIET PROFILE</div>
          <div style="color:#E2E8F0"><b>Type:</b> {profile.get('dietary_pref')}</div>
          <div style="color:#E2E8F0"><b>Cuisine:</b> {profile.get('cultural_bg')}</div>
          <div style="color:#E2E8F0"><b>Budget:</b> ₹{profile.get('budget_inr')}/day</div>
          <div style="color:#E2E8F0"><b>Goal:</b> {profile.get('goal')}</div>
        </div>
        """, unsafe_allow_html=True)
        gen_diet_btn = st.button("🤖 Generate AI Diet Plan", use_container_width=True, type="primary")
        if existing_diet:
            st.caption("✅ Plan exists — click to regenerate")

    with info_col:
        if not existing_diet:
            st.info("Click **Generate AI Diet Plan** to get a culturally appropriate, budget-friendly 7-day meal plan powered by Gemini AI.")

    if gen_diet_btn:
        if not check_api_key():
            st.stop()
        with st.spinner("🤖 Gemini is creating your personalized meal plan..."):
            try:
                plan = generate_diet_plan(profile, macros)
                save_plan("diet", plan)
                st.success("✅ Your 7-day diet plan has been generated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating diet plan: {e}")

    if existing_diet:
        st.markdown("---")
        # Parse by day
        days_content = {}
        current_day = None
        current_content = []

        for line in existing_diet.split("\n"):
            if line.strip().startswith("## "):
                if current_day and current_content:
                    days_content[current_day] = "\n".join(current_content)
                current_day = line.strip()[3:]
                current_content = []
            elif current_day:
                current_content.append(line)

        if current_day and current_content:
            days_content[current_day] = "\n".join(current_content)

        if days_content:
            selected_day = st.selectbox("📅 Select Day", list(days_content.keys()))
            if selected_day and selected_day in days_content:
                st.markdown(f"""
                <div class="meal-card">
                  <h3 style="color:#00C9A7;margin:0 0 8px">🥗 {selected_day}</h3>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(days_content[selected_day])

        with st.expander("📄 View Full Plan (Raw)"):
            st.markdown(existing_diet)

        # Recipe AI suggestion
        st.markdown("---")
        st.markdown("### 🍳 Get a Quick Recipe")
        r1, r2 = st.columns([3, 1])
        with r1:
            recipe_query = st.text_input("Ask for a recipe...", placeholder="e.g., Dal Tadka, Oatmeal with banana, Paneer bhurji...")
        with r2:
            recipe_btn = st.button("🤖 Get Recipe", use_container_width=True)

        if recipe_btn and recipe_query:
            if check_api_key():
                with st.spinner("Getting recipe..."):
                    try:
                        recipe = get_recipe_suggestion(recipe_query, profile.get("dietary_pref", ""), profile.get("budget_inr", 200) / 3)
                        st.markdown(f"""<div class="glass-card">{recipe}</div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LOG TODAY
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "📓 Log Today":
    st.markdown("## 📓 Log Today")

    profile = get_profile()
    log_date = st.date_input("Date", value=datetime.date.today())
    log_date_str = str(log_date)

    tab_meal, tab_workout, tab_weight = st.tabs(["🍽️ Log Meal", "💪 Log Workout", "⚖️ Log Weight"])

    # ── Meal Log ──
    with tab_meal:
        st.markdown("### 🍽️ Log a Meal")

        log_col, db_col = st.columns([3, 2])

        with db_col:
            st.markdown("#### 🔍 Food Database")
            search = st.text_input("Search food...", placeholder="Type to search...", key="food_search")

            dietary_filter = profile.get("dietary_pref", "Non-Vegetarian") if profile else "All"
            filtered_foods = [
                f for f in FOOD_DB
                if (not search or search.lower() in f["name"].lower())
                and (dietary_filter == "All" or dietary_filter in f.get("dietary", []))
            ]

            if filtered_foods:
                for food in filtered_foods[:8]:
                    with st.expander(f"**{food['name']}** — {food['calories_per_100g']} kcal/100g"):
                        st.markdown(f"""
                        **P:** {food['protein']}g | **C:** {food['carbs']}g | **F:** {food['fat']}g  
                        **Cost:** ~₹{food['cost_per_100g_inr']}/100g  
                        **Category:** {food['category']}
                        """)

        with log_col:
            with st.form("meal_log_form"):
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Mid-Morning Snack", "Lunch", "Evening Snack", "Dinner", "Other"])

                # Option: use from DB or manual
                use_db = st.checkbox("Select from Food Database", value=False)

                if use_db and filtered_foods:
                    food_names = [f["name"] for f in FOOD_DB]
                    selected_food_name = st.selectbox("Select Food", food_names)
                    selected_food = next((f for f in FOOD_DB if f["name"] == selected_food_name), None)
                    qty = st.number_input("Quantity (grams)", min_value=10.0, max_value=2000.0, value=100.0, step=10.0)

                    if selected_food:
                        factor = qty / 100
                        food_name = selected_food_name
                        calories = round(selected_food["calories_per_100g"] * factor, 1)
                        protein = round(selected_food["protein"] * factor, 1)
                        carbs = round(selected_food["carbs"] * factor, 1)
                        fat = round(selected_food["fat"] * factor, 1)

                        st.markdown(f"""
                        <div style="background:rgba(0,201,167,0.05);border:1px solid rgba(0,201,167,0.2);
                             border-radius:10px;padding:12px;margin:8px 0">
                          <span style="color:#94A3B8">Calculated for {qty}g:</span><br>
                          🔥 <b style="color:#00C9A7">{calories} kcal</b> | 
                          P: <b>{protein}g</b> | C: <b>{carbs}g</b> | F: <b>{fat}g</b>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    food_name = st.text_input("Food Name *", placeholder="e.g., Dal Rice, Banana, Dosa")
                    qty = st.number_input("Quantity (grams)", min_value=10.0, max_value=2000.0, value=100.0, step=10.0)
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        calories = st.number_input("Calories (kcal)", min_value=0.0, value=0.0, step=1.0)
                        protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
                    with mc2:
                        carbs = st.number_input("Carbs (g)", min_value=0.0, value=0.0, step=0.1)
                        fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, step=0.1)

                notes = st.text_input("Notes (optional)", placeholder="e.g., homemade, extra spicy...")
                submit_meal = st.form_submit_button("✅ Log Meal", use_container_width=True)

                if submit_meal and food_name:
                    log_meal(log_date_str, meal_type, food_name, calories, protein, carbs, fat, qty, notes)
                    st.success(f"✅ Logged: {food_name} ({calories:.0f} kcal)")
                    st.rerun()

        # Show today's meals
        st.markdown("---")
        st.markdown(f"### 📋 Meals Logged for {log_date.strftime('%d %b %Y')}")
        meals = get_meals_for_date(log_date_str)

        if meals:
            total_cal = sum(m["calories"] for m in meals)
            total_p = sum(m["protein"] for m in meals)
            total_c = sum(m["carbs"] for m in meals)
            total_f = sum(m["fat"] for m in meals)

            st.markdown(f"""
            <div class="glass-card">
              <div style="display:flex;gap:32px;flex-wrap:wrap">
                <div><div style="color:#64748B;font-size:0.75rem">Total Calories</div>
                     <div style="color:#00C9A7;font-size:1.5rem;font-weight:700">{total_cal:.0f} kcal</div></div>
                <div><div style="color:#64748B;font-size:0.75rem">Protein</div>
                     <div style="color:#E2E8F0;font-size:1.3rem;font-weight:600">{total_p:.0f}g</div></div>
                <div><div style="color:#64748B;font-size:0.75rem">Carbs</div>
                     <div style="color:#E2E8F0;font-size:1.3rem;font-weight:600">{total_c:.0f}g</div></div>
                <div><div style="color:#64748B;font-size:0.75rem">Fat</div>
                     <div style="color:#E2E8F0;font-size:1.3rem;font-weight:600">{total_f:.0f}g</div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            for m in meals:
                mc1, mc2, mc3 = st.columns([4, 3, 1])
                with mc1:
                    st.markdown(f"🍽️ **{m['food_name']}** _{m['meal_type']}_")
                with mc2:
                    st.markdown(f"<span style='color:#00C9A7'>{m['calories']:.0f} kcal</span> | P:{m['protein']:.0f}g C:{m['carbs']:.0f}g F:{m['fat']:.0f}g", unsafe_allow_html=True)
                with mc3:
                    if st.button("🗑️", key=f"del_meal_{m['id']}"):
                        delete_meal_log(m["id"])
                        st.rerun()
        else:
            st.info("No meals logged yet for this date.")

    # ── Workout Log ──
    with tab_workout:
        st.markdown("### 💪 Log a Workout")

        with st.form("workout_log_form"):
            wc1, wc2 = st.columns(2)
            with wc1:
                exercise_name = st.text_input("Exercise Name *", placeholder="e.g., Push-ups, Running, Squats")
                sets = st.number_input("Sets", min_value=0, max_value=20, value=3)
                reps = st.number_input("Reps per Set", min_value=0, max_value=100, value=10)
            with wc2:
                duration_min = st.number_input("Duration (minutes)", min_value=0, max_value=300, value=0)
                calories_burned = st.number_input("Estimated Calories Burned", min_value=0.0, value=0.0, step=1.0)
                workout_notes = st.text_input("Notes", placeholder="e.g., felt strong today, increased weight...")

            submit_workout = st.form_submit_button("✅ Log Workout", use_container_width=True)

            if submit_workout and exercise_name:
                log_workout(log_date_str, exercise_name, sets, reps, duration_min, calories_burned, workout_notes)
                st.success(f"✅ Logged: {exercise_name}")
                st.rerun()

        st.markdown("---")
        st.markdown(f"### 📋 Workouts for {log_date.strftime('%d %b %Y')}")
        workouts = get_workouts_for_date(log_date_str)

        if workouts:
            for w in workouts:
                wc1, wc2, wc3 = st.columns([4, 3, 1])
                with wc1:
                    st.markdown(f"💪 **{w['exercise_name']}**")
                with wc2:
                    st.markdown(f"{w.get('sets',0)}×{w.get('reps',0)} | ⏱ {w.get('duration_min',0)}min | 🔥 {w.get('calories_burned',0):.0f} kcal")
                with wc3:
                    if st.button("🗑️", key=f"del_wo_{w['id']}"):
                        delete_workout_log(w["id"])
                        st.rerun()
        else:
            st.info("No workout logged yet for this date.")

    # ── Weight Log ──
    with tab_weight:
        st.markdown("### ⚖️ Log Your Weight")

        with st.form("weight_form"):
            w1, w2 = st.columns(2)
            with w1:
                new_weight = st.number_input("Weight (kg) *", min_value=20.0, max_value=300.0,
                                             value=float(profile["weight_kg"]) if profile else 70.0, step=0.1)
            with w2:
                weight_note = st.text_input("Note (optional)", placeholder="e.g., morning measurement")
            submit_weight = st.form_submit_button("✅ Log Weight", use_container_width=True)

            if submit_weight:
                log_weight(log_date_str, new_weight, weight_note)
                st.success(f"✅ Weight logged: {new_weight} kg")
                st.rerun()

        st.markdown("---")
        weight_hist = get_weight_history()
        if weight_hist:
            df_w = pd.DataFrame(weight_hist)
            st.markdown("### 📈 Weight History")
            fig_w = weight_chart(weight_hist)
            if fig_w:
                st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": False})
            st.dataframe(
                df_w[["log_date", "weight_kg", "notes"]].rename(columns={"log_date": "Date", "weight_kg": "Weight (kg)", "notes": "Notes"}),
                use_container_width=True, hide_index=True
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PROGRESS
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "📊 Progress":
    st.markdown("## 📊 Progress Tracker")

    profile = get_profile()
    if not profile:
        st.warning("Complete your profile first!")
        st.stop()

    streak = get_streak()
    weekly = get_weekly_summary()
    weight_hist = get_weight_history(30)

    # ── Top Stats ──
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("🔥 Current Streak", f"{streak} days")
    s2.metric("📅 Weekly Calories", f"{weekly['calories_consumed']:.0f} kcal")
    s3.metric("💪 Workout Time", f"{weekly['workout_minutes']} min")
    s4.metric("🏃 Calories Burned", f"{weekly['calories_burned']:.0f} kcal")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚖️ Weight Trend (Last 30 Days)")
        if weight_hist:
            fig_w = weight_chart(weight_hist)
            if fig_w:
                st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": False})

            if len(weight_hist) >= 2:
                change = weight_hist[-1]["weight_kg"] - weight_hist[0]["weight_kg"]
                dir_icon = "📉" if change < 0 else "📈"
                color = "#00C9A7" if (change < 0 and profile.get("goal") == "Lose Weight") else "#FF6B6B"
                st.markdown(f"""
                <div style="text-align:center;padding:12px;background:rgba(0,0,0,0.2);border-radius:12px">
                  <span style="color:#94A3B8">Weight Change: </span>
                  <span style="color:{color};font-weight:700">{dir_icon} {change:+.1f} kg</span>
                  <span style="color:#64748B"> over {len(weight_hist)} days</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Start logging your weight daily to see trends!")

    with col2:
        st.markdown("### 📊 This Week's Macros")
        if weekly["calories_consumed"] > 0:
            bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
            tdee = calculate_tdee(bmr, profile["activity_level"])
            macros = get_macro_targets(tdee, profile["goal"])

            render_macro_bar("Protein", weekly["protein"] / 7, macros["protein_g"], "protein")
            render_macro_bar("Carbs", weekly["carbs"] / 7, macros["carbs_g"], "carbs")
            render_macro_bar("Fat", weekly["fat"] / 7, macros["fat_g"], "fat")

            avg_cal = weekly["calories_consumed"] / 7
            st.markdown(f"""
            <div style="margin-top:16px;text-align:center">
              <div style="color:#64748B;font-size:0.8rem">Average daily intake this week</div>
              <div style="color:#00C9A7;font-size:2rem;font-weight:800">{avg_cal:.0f} kcal</div>
              <div style="color:#64748B;font-size:0.8rem">Target: {macros['calories']} kcal/day</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Log your meals to see macro breakdown!")

    # ── AI Progress Analysis ──
    st.markdown("---")
    st.markdown("### 🤖 AI Progress Analysis")

    if st.button("🔍 Analyze My Progress with AI", use_container_width=True):
        if check_api_key():
            with st.spinner("Analyzing your progress..."):
                try:
                    analysis = analyze_progress(profile, weight_hist, weekly)
                    st.markdown(f"""<div class="glass-card">{analysis}</div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI COACH
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "🤖 AI Coach":
    st.markdown("## 🤖 FitBot — Your AI Fitness Coach")
    st.markdown("<p style='color:#94A3B8'>Ask me anything about fitness, nutrition, motivation, or your plan!</p>", unsafe_allow_html=True)

    profile = get_profile()
    if not profile:
        st.warning("Complete your profile first for personalized advice!")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:32px">
              <div style="font-size:3rem;margin-bottom:12px">🤖</div>
              <div style="color:#94A3B8;font-size:1rem">
                Hi! I'm FitBot, your personal AI fitness coach.<br>
                Ask me anything — workouts, nutrition, motivation, or your plan!
              </div>
              <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
                <span style="background:rgba(0,201,167,0.1);border:1px solid rgba(0,201,167,0.2);color:#94A3B8;padding:6px 14px;border-radius:20px;font-size:0.8rem;cursor:pointer">💪 How to improve push-ups?</span>
                <span style="background:rgba(0,201,167,0.1);border:1px solid rgba(0,201,167,0.2);color:#94A3B8;padding:6px 14px;border-radius:20px;font-size:0.8rem">🥗 Best protein sources under ₹50?</span>
                <span style="background:rgba(0,201,167,0.1);border:1px solid rgba(0,201,167,0.2);color:#94A3B8;padding:6px 14px;border-radius:20px;font-size:0.8rem">😴 Does sleep affect weight loss?</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin:8px 0">
                  <div style="background:linear-gradient(135deg,#00C9A7,#00A886);color:#0A0E1A;
                       border-radius:18px 18px 4px 18px;padding:12px 16px;max-width:70%;font-weight:500">
                    {msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin:8px 0">
                  <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(0,201,167,0.2);
                       color:#E2E8F0;border-radius:18px 18px 18px 4px;padding:12px 16px;max-width:75%">
                    <span style="color:#00C9A7;font-size:0.75rem;font-weight:600">🤖 FitBot</span><br>
                    {msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Chat input
    chat_col, btn_col = st.columns([5, 1])
    with chat_col:
        user_msg = st.text_input(
            "Message FitBot...",
            placeholder="Ask about workouts, nutrition, motivation...",
            label_visibility="collapsed",
            key="chat_input"
        )
    with btn_col:
        send_btn = st.button("Send 🚀", use_container_width=True)

    if (send_btn or user_msg) and user_msg:
        if check_api_key():
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            with st.spinner("FitBot is thinking..."):
                try:
                    response = chat_with_coach(user_msg, profile or {}, st.session_state.chat_history)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXPORT PDF
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "📄 Export PDF":
    st.markdown("## 📄 Export Your Plan as PDF")
    st.markdown("<p style='color:#94A3B8'>Download your complete personalized workout and diet plan as a beautifully formatted PDF.</p>", unsafe_allow_html=True)

    profile = get_profile()
    if not profile:
        st.warning("Complete your profile first!")
        st.stop()

    workout_plan = load_plan("workout")
    diet_plan = load_plan("diet")

    # Status check
    col1, col2, col3 = st.columns(3)
    with col1:
        if profile:
            st.success("✅ Profile: Ready")
        else:
            st.error("❌ Profile: Missing")
    with col2:
        if workout_plan:
            st.success("✅ Workout Plan: Ready")
        else:
            st.warning("⚠️ Workout Plan: Not Generated")
    with col3:
        if diet_plan:
            st.success("✅ Diet Plan: Ready")
        else:
            st.warning("⚠️ Diet Plan: Not Generated")

    if not workout_plan or not diet_plan:
        st.info("💡 Generate your AI plans (Workout & Diet) before exporting.")

    st.markdown("---")

    if profile:
        bmi = calculate_bmi(profile["weight_kg"], profile["height_cm"])
        cat, _ = get_bmi_category(bmi)
        bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
        tdee = calculate_tdee(bmr, profile["activity_level"])
        macros = get_macro_targets(tdee, profile["goal"])

        if st.button("📥 Generate & Download PDF", use_container_width=True, type="primary",
                     disabled=(not workout_plan or not diet_plan)):
            try:
                from modules.pdf_exporter import export_plan_pdf
                with st.spinner("Generating your PDF..."):
                    pdf_path = export_plan_pdf(
                        profile=profile,
                        workout_plan=workout_plan or "Workout plan not generated.",
                        diet_plan=diet_plan or "Diet plan not generated.",
                        macro_targets=macros,
                        bmi=bmi,
                        bmi_category=cat,
                        tdee=tdee,
                    )

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="📄 Download PDF Now",
                    data=pdf_bytes,
                    file_name=f"FitAI_Plan_{profile.get('name', 'Student').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.success("✅ PDF generated! Click the button above to download.")
                st.balloons()

            except Exception as e:
                st.error(f"Error generating PDF: {e}")
                st.exception(e)

        # Preview
        st.markdown("### 📋 PDF Preview")
        st.markdown(f"""
        <div class="glass-card">
          <div style="font-size:1.4rem;font-weight:800;color:#00C9A7;margin-bottom:8px">💪 FitAI Planner</div>
          <div style="color:#94A3B8;margin-bottom:16px">Your Personalized Fitness & Nutrition Blueprint</div>
          <hr style="border-color:rgba(255,255,255,0.1)">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px">
            <div><span style="color:#64748B">Name:</span> <b style="color:#E2E8F0">{profile.get('name')}</b></div>
            <div><span style="color:#64748B">Goal:</span> <b style="color:#00C9A7">{profile.get('goal')}</b></div>
            <div><span style="color:#64748B">Diet:</span> <b style="color:#E2E8F0">{profile.get('dietary_pref')}</b></div>
            <div><span style="color:#64748B">Cuisine:</span> <b style="color:#E2E8F0">{profile.get('cultural_bg')}</b></div>
            <div><span style="color:#64748B">BMI:</span> <b style="color:#00C9A7">{bmi} ({cat})</b></div>
            <div><span style="color:#64748B">Calories:</span> <b style="color:#00C9A7">{macros['calories']} kcal/day</b></div>
          </div>
          <hr style="border-color:rgba(255,255,255,0.1);margin-top:12px">
          <div style="color:#64748B;font-size:0.8rem">Includes: ✅ 7-Day Workout Plan | ✅ 7-Day Meal Plan | ✅ Health Metrics | ✅ Macro Targets</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "Settings":
    st.markdown("## Settings")
    
    tab1, tab2 = st.tabs(["API Key", "Account"])
    
    with tab1:
        st.markdown("### Groq API Keyy")
        st.info("Your API key is encrypted and stored securely. It will never be shared or logged.")
        
        with st.form("api_key_form"):
            new_api_key = st.text_input(
                "Enter Your Groq API Key",
                type="password",
                placeholder="Get a free key from https://aistudio.google.com/",
                help="Your key is encrypted before storage"
            )
            
            if st.form_submit_button("Save API Key", use_container_width=True):
                if not new_api_key:
                    st.error("Please enter an API key")
                else:
                    try:
                        # Encrypt and save
                        encrypted_key = encrypt_api_key(new_api_key)
                        save_api_key(st.session_state.user["id"], encrypted_key)
                        st.session_state.api_key = new_api_key
                        st.success("API key saved securely!")
                    except Exception as e:
                        st.error(f"Error saving API key: {e}")
        
        # Show status
        if get_api_key(st.session_state.user["id"]):
            st.success("API key is configured and encrypted")
        else:
            st.warning("No API key configured yet")
    
    with tab2:
        st.markdown("### Account Information")
        st.text_input("Email", value=st.session_state.user["email"], disabled=True)
        st.text_input("Full Name", value=st.session_state.user.get("full_name", ""), disabled=True)
        
        st.markdown("### Danger Zone")
        if st.button("Delete Account", type="secondary"):
           st.session_state.clear()
           st.success("Account deleted successfully!")
           st.rerun()

