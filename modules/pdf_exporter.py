"""
PDF Export Module
Generates a formatted PDF report of the user's personalized plan.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Color Palette
PRIMARY = colors.HexColor("#00C9A7")
SECONDARY = colors.HexColor("#845EC2")
ACCENT = colors.HexColor("#FF6B6B")
DARK_BG = colors.HexColor("#0A0E1A")
LIGHT_GRAY = colors.HexColor("#F0F4F8")
DARK_TEXT = colors.HexColor("#1A202C")
MID_GRAY = colors.HexColor("#718096")


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="AppTitle",
        fontSize=28,
        textColor=PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        leading=34,
    ))
    styles.add(ParagraphStyle(
        name="AppSubtitle",
        fontSize=13,
        textColor=MID_GRAY,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=18,
        textColor=SECONDARY,
        spaceBefore=20,
        spaceAfter=8,
        fontName="Helvetica-Bold",
        borderPad=6,
    ))
    styles.add(ParagraphStyle(
        name="DayHeader",
        fontSize=14,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=10,
        textColor=DARK_TEXT,
        spaceAfter=4,
        fontName="Helvetica",
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="SmallGray",
        fontSize=9,
        textColor=MID_GRAY,
        spaceAfter=2,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="MetricLabel",
        fontSize=10,
        textColor=MID_GRAY,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="MetricValue",
        fontSize=14,
        textColor=PRIMARY,
        fontName="Helvetica-Bold",
    ))

    return styles


def export_plan_pdf(profile: dict, workout_plan: str, diet_plan: str,
                    macro_targets: dict, bmi: float, bmi_category: str,
                    tdee: int, output_path: str = None) -> str:
    """
    Generate a complete PDF plan document.
    Returns the path of the saved PDF file.
    """
    if output_path is None:
        name = profile.get("name", "Student").replace(" ", "_")
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            f"FitAI_Plan_{name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    styles = create_styles()
    story = []

    # ─── Cover Page ───────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("💪 FitAI Planner", styles["AppTitle"]))
    story.append(Paragraph("Your Personalized Fitness & Nutrition Blueprint", styles["AppSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=16))

    # Profile Summary Table
    story.append(Paragraph("👤 Your Profile", styles["SectionHeader"]))

    profile_data = [
        ["Name", profile.get("name", "—"), "Age", f"{profile.get('age')} years"],
        ["Gender", profile.get("gender", "—"), "Height", f"{profile.get('height_cm')} cm"],
        ["Weight", f"{profile.get('weight_kg')} kg", "Goal", profile.get("goal", "—")],
        ["Diet Preference", profile.get("dietary_pref", "—"), "Cultural Background", profile.get("cultural_bg", "—")],
        ["Activity Level", profile.get("activity_level", "—"), "Equipment", profile.get("equipment", "—")],
        ["Fitness Level", profile.get("fitness_level", "—"), "Daily Budget", f"₹{profile.get('budget_inr', 200)}"],
    ]

    profile_table = Table(profile_data, colWidths=[3.5 * cm, 5.5 * cm, 3.5 * cm, 5.5 * cm])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK_TEXT),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FFFE")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 0.5 * cm))

    # ─── Health Metrics ───────────────────────────────────
    story.append(Paragraph("📊 Health Metrics", styles["SectionHeader"]))

    metrics_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["BMI", f"{bmi}", "BMI Category", bmi_category],
        ["Daily Calorie Target", f"{macro_targets.get('calories', 0)} kcal", "TDEE", f"{tdee} kcal"],
        ["Daily Protein", f"{macro_targets.get('protein_g', 0)}g", "Daily Carbs", f"{macro_targets.get('carbs_g', 0)}g"],
        ["Daily Fat", f"{macro_targets.get('fat_g', 0)}g", "Fitness Goal", profile.get("goal", "—")],
    ]

    metrics_table = Table(metrics_data, colWidths=[4.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (1, 1), (1, -1), PRIMARY),
        ("TEXTCOLOR", (3, 1), (3, -1), PRIMARY),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(metrics_table)

    story.append(PageBreak())

    # ─── Workout Plan ─────────────────────────────────────
    story.append(Paragraph("💪 Your 7-Day Workout Plan", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    # Parse and render workout plan
    _render_markdown_to_pdf(workout_plan, story, styles)

    story.append(PageBreak())

    # ─── Diet Plan ────────────────────────────────────────
    story.append(Paragraph("🥗 Your 7-Day Meal Plan", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    _render_markdown_to_pdf(diet_plan, story, styles)

    # ─── Footer Note ─────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=8))
    story.append(Paragraph(
        f"Generated by FitAI Planner on {datetime.now().strftime('%d %B %Y')} | "
        "This plan is AI-generated. Consult a healthcare professional before starting any new fitness or diet regimen.",
        styles["SmallGray"]
    ))

    doc.build(story)
    return output_path


def _render_markdown_to_pdf(text: str, story: list, styles):
    """Convert markdown text to ReportLab PDF elements."""
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2 * cm))
            continue

        # Headers
        if line.startswith("## "):
            story.append(Paragraph(line[3:], styles["DayHeader"]))
        elif line.startswith("### "):
            p_style = ParagraphStyle(
                name="SubHeader", fontSize=11, textColor=SECONDARY,
                fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3
            )
            story.append(Paragraph(line[4:], p_style))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], styles["SectionHeader"]))
        elif line.startswith("**") and line.endswith("**"):
            p_style = ParagraphStyle(
                name="BoldLine", fontSize=10, textColor=DARK_TEXT,
                fontName="Helvetica-Bold", spaceAfter=3
            )
            story.append(Paragraph(line.strip("*"), p_style))
        elif line.startswith("- ") or line.startswith("* "):
            clean = line[2:]
            # Handle bold in bullet
            clean = clean.replace("**", "<b>", 1).replace("**", "</b>", 1)
            p_style = ParagraphStyle(
                name="Bullet", fontSize=9, textColor=DARK_TEXT,
                fontName="Helvetica", leftIndent=12, spaceAfter=2,
                bulletText="•"
            )
            story.append(Paragraph(f"• {clean}", styles["BodyText2"]))
        elif line.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))
        else:
            # Regular text - clean up markdown bold
            clean = line.replace("**", "")
            story.append(Paragraph(clean, styles["BodyText2"]))
