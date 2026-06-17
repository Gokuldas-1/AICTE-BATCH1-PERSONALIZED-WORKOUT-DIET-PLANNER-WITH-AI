"""
BMI & Health Metrics Calculator
"""

from config.settings import ACTIVITY_MULTIPLIERS


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def get_bmi_category(bmi: float) -> tuple[str, str]:
    """Returns (category, emoji)"""
    if bmi < 18.5:
        return "Underweight", "🔵"
    elif bmi < 25.0:
        return "Normal Weight", "🟢"
    elif bmi < 30.0:
        return "Overweight", "🟡"
    else:
        return "Obese", "🔴"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor BMR formula"""
    if gender.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Total Daily Energy Expenditure"""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier)


def get_macro_targets(tdee: float, goal: str) -> dict:
    """Return daily macro targets in grams based on goal."""
    if goal == "Lose Weight":
        calories_target = tdee - 500
        protein_pct, carb_pct, fat_pct = 0.35, 0.35, 0.30
    elif goal == "Gain Muscle":
        calories_target = tdee + 300
        protein_pct, carb_pct, fat_pct = 0.30, 0.45, 0.25
    elif goal == "Build Strength":
        calories_target = tdee + 200
        protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
    else:
        calories_target = tdee
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25

    calories_target = max(calories_target, 1200)

    return {
        "calories": round(calories_target),
        "protein_g": round((calories_target * protein_pct) / 4),
        "carbs_g": round((calories_target * carb_pct) / 4),
        "fat_g": round((calories_target * fat_pct) / 9),
    }


def get_ideal_weight_range(height_cm: float) -> tuple[float, float]:
    """Returns (min_kg, max_kg) based on healthy BMI 18.5–24.9"""
    h = height_cm / 100
    return round(18.5 * h * h, 1), round(24.9 * h * h, 1)


def get_water_intake(weight_kg: float, activity_level: str) -> float:
    """Recommended daily water intake in liters"""
    base = weight_kg * 0.033
    if "Very active" in activity_level or "Extra active" in activity_level:
        base += 0.5
    elif "Moderately" in activity_level:
        base += 0.3
    return round(base, 1)
