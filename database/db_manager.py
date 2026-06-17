"""
SQLite Database Manager
Handles all CRUD operations for the FitAI Planner app.
"""

import sqlite3
import json
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fitai.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS user_api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            encrypted_api_key TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            goal TEXT,
            dietary_pref TEXT,
            cultural_bg TEXT,
            activity_level TEXT,
            equipment TEXT,
            fitness_level TEXT,
            budget_inr REAL,
            allergies TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS generated_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_type TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS meal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT,
            meal_type TEXT,
            food_name TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            quantity_g REAL,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT,
            exercise_name TEXT,
            sets INTEGER,
            reps INTEGER,
            duration_min INTEGER,
            calories_burned REAL,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT,
            weight_kg REAL,
            notes TEXT,
            UNIQUE(user_id, log_date),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


# --- User Profile ---

def save_profile(profile: dict):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("SELECT id FROM user_profile WHERE id = 1")
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE user_profile SET
                name=?, age=?, gender=?, height_cm=?, weight_kg=?, goal=?,
                dietary_pref=?, cultural_bg=?, activity_level=?, equipment=?,
                fitness_level=?, budget_inr=?, allergies=?, updated_at=?
            WHERE id = 1
        """, (
            profile.get("name"), profile.get("age"), profile.get("gender"),
            profile.get("height_cm"), profile.get("weight_kg"), profile.get("goal"),
            profile.get("dietary_pref"), profile.get("cultural_bg"),
            profile.get("activity_level"), profile.get("equipment"),
            profile.get("fitness_level"), profile.get("budget_inr"),
            profile.get("allergies"), now
        ))
    else:
        cursor.execute("""
            INSERT INTO user_profile
                (id, name, age, gender, height_cm, weight_kg, goal,
                 dietary_pref, cultural_bg, activity_level, equipment,
                 fitness_level, budget_inr, allergies, created_at, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.get("name"), profile.get("age"), profile.get("gender"),
            profile.get("height_cm"), profile.get("weight_kg"), profile.get("goal"),
            profile.get("dietary_pref"), profile.get("cultural_bg"),
            profile.get("activity_level"), profile.get("equipment"),
            profile.get("fitness_level"), profile.get("budget_inr"),
            profile.get("allergies"), now, now
        ))

    conn.commit()
    conn.close()


def load_profile() -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# --- Generated Plans ---

def save_plan(plan_type: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM generated_plans WHERE plan_type = ?", (plan_type,))
    cursor.execute(
        "INSERT INTO generated_plans (plan_type, content, created_at) VALUES (?, ?, ?)",
        (plan_type, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def load_plan(plan_type: str) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM generated_plans WHERE plan_type = ?", (plan_type,))
    row = cursor.fetchone()
    conn.close()
    return row["content"] if row else None


# --- Meal Logs ---

def log_meal(log_date: str, meal_type: str, food_name: str, calories: float,
             protein: float, carbs: float, fat: float, quantity_g: float = 100, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meal_logs (log_date, meal_type, food_name, calories, protein, carbs, fat, quantity_g, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (log_date, meal_type, food_name, calories, protein, carbs, fat, quantity_g, notes))
    conn.commit()
    conn.close()


def get_meals_for_date(log_date: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meal_logs WHERE log_date = ? ORDER BY id", (log_date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_meal_log(log_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meal_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


# --- Workout Logs ---

def log_workout(log_date: str, exercise_name: str, sets: int = 0, reps: int = 0,
                duration_min: int = 0, calories_burned: float = 0, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workout_logs (log_date, exercise_name, sets, reps, duration_min, calories_burned, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (log_date, exercise_name, sets, reps, duration_min, calories_burned, notes))
    conn.commit()
    conn.close()


def get_workouts_for_date(log_date: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout_logs WHERE log_date = ? ORDER BY id", (log_date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_workout_log(log_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workout_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


# --- Weight Logs ---

def log_weight(log_date: str, weight_kg: float, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO weight_logs (log_date, weight_kg, notes)
        VALUES (?, ?, ?)
    """, (log_date, weight_kg, notes))
    conn.commit()
    conn.close()


def get_weight_history(limit: int = 30) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weight_logs ORDER BY log_date DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def get_streak() -> int:
    """Count consecutive days with workout logs up to today."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT log_date FROM workout_logs ORDER BY log_date DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    streak = 0
    today = date.today()
    for i, row in enumerate(rows):
        expected = str(today - __import__('datetime').timedelta(days=i))
        if row["log_date"] == expected:
            streak += 1
        else:
            break
    return streak


def get_weekly_summary() -> dict:
    """Get totals for the current week."""
    import datetime as dt
    conn = get_connection()
    cursor = conn.cursor()

    today = dt.date.today()
    week_start = today - dt.timedelta(days=today.weekday())
    week_end = today

    cursor.execute("""
        SELECT SUM(calories) as total_cal, SUM(protein) as total_protein,
               SUM(carbs) as total_carbs, SUM(fat) as total_fat
        FROM meal_logs WHERE log_date BETWEEN ? AND ?
    """, (str(week_start), str(week_end)))
    meal_row = cursor.fetchone()

    cursor.execute("""
        SELECT SUM(calories_burned) as total_burned, SUM(duration_min) as total_min
        FROM workout_logs WHERE log_date BETWEEN ? AND ?
    """, (str(week_start), str(week_end)))
    workout_row = cursor.fetchone()

    conn.close()

    return {
        "calories_consumed": meal_row["total_cal"] or 0,
        "protein": meal_row["total_protein"] or 0,
        "carbs": meal_row["total_carbs"] or 0,
        "fat": meal_row["total_fat"] or 0,
        "calories_burned": workout_row["total_burned"] or 0,
        "workout_minutes": workout_row["total_min"] or 0,
    }


# --- User Authentication ---

def register_user(email: str, password_hash: str, full_name: str) -> dict | None:
    """Register a new user. Returns user dict with id on success, None if email exists."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (email, password_hash, full_name, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "email": email, "full_name": full_name}
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_email(email: str) -> dict | None:
    """Get user by email for login."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password_hash, full_name FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# --- API Key Management (Encrypted) ---

def save_api_key(user_id: int, encrypted_api_key: str):
    """Save encrypted API key for user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_api_keys WHERE user_id = ?", (user_id,))
    cursor.execute("""
        INSERT INTO user_api_keys (user_id, encrypted_api_key, created_at)
        VALUES (?, ?, ?)
    """, (user_id, encrypted_api_key, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_api_key(user_id: int) -> str | None:
    """Get encrypted API key for user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_api_key FROM user_api_keys WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["encrypted_api_key"] if row else None

