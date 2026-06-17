"""
App Configuration Settings
"""

APP_NAME = "FitAI Planner"
APP_VERSION = "1.0.0"
APP_ICON = "💪"

# AI Model Configuration
# AI Model Configuration
GEMINI_MODEL = "gemini-2.0-flash"  # Updated to the latest Gemini model
MAX_OUTPUT_TOKENS = 4096
TEMPERATURE = 0.7

# Health Constants
BMI_CATEGORIES = {
    "Underweight": (0, 18.5),
    "Normal weight": (18.5, 25.0),
    "Overweight": (25.0, 30.0),
    "Obese": (30.0, float("inf")),
}

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little or no exercise)": 1.2,
    "Lightly active (1-3 days/week)": 1.375,
    "Moderately active (3-5 days/week)": 1.55,
    "Very active (6-7 days/week)": 1.725,
    "Extra active (physical job + exercise)": 1.9,
}

FITNESS_GOALS = [
    "Lose Weight",
    "Gain Muscle",
    "Maintain Weight",
    "Improve Stamina",
    "Build Strength",
    "Improve Flexibility",
]

DIETARY_PREFERENCES = [
    "Non-Vegetarian",
    "Vegetarian",
    "Vegan",
    "Jain (No root vegetables)",
    "Halal",
    "Eggetarian",
    "Keto",
    "Gluten-Free",
]

CULTURAL_BACKGROUNDS = [
    "North Indian",
    "South Indian",
    "Bengali / East Indian",
    "Gujarati / Rajasthani",
    "Maharashtrian",
    "Western / Continental",
    "Mediterranean",
    "Pan Asian",
    "No preference",
]

EQUIPMENT_OPTIONS = [
    "No Equipment (Bodyweight only)",
    "Resistance Bands",
    "Dumbbells at Home",
    "Full Home Gym",
    "Commercial Gym Access",
]

FITNESS_LEVELS = [
    "Beginner (0-6 months experience)",
    "Intermediate (6 months - 2 years)",
    "Advanced (2+ years)",
]

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Color Theme
COLORS = {
    "primary": "#00C9A7",
    "secondary": "#845EC2",
    "accent": "#FF6B6B",
    "bg_dark": "#0A0E1A",
    "bg_card": "#111827",
    "text_light": "#E2E8F0",
}
