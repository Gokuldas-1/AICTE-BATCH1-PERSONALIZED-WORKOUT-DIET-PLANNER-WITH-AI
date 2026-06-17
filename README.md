# Personalized Workout & Diet Planner with AI

## Overview

The Personalized Workout & Diet Planner with AI is an intelligent fitness management application developed using Python and Streamlit. The system generates customized workout routines and diet plans based on user health data, fitness goals, dietary preferences, lifestyle, and budget constraints.

Unlike traditional fitness applications that provide generic recommendations, this platform uses AI to deliver personalized and practical fitness guidance for each user.

---

## Features

- User Profile Management
- BMI Calculator
- Personalized Workout Planning
- Personalized Diet Recommendations
- AI-Powered Fitness Suggestions
- Budget-Friendly Meal Planning
- Progress Tracking
- PDF Report Generation
- SQLite Database Integration
- Streamlit Interactive Dashboard

---

## Technologies Used

### Frontend
- Streamlit

### Backend
- Python

### Database
- SQLite

### Libraries
- Pandas
- NumPy
- Matplotlib
- Streamlit
- Python-dotenv

---

## Project Structure

```text
DietPlan/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── assets/
├── config/
├── database/
├── data/
└── modules/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Gokuldas-1/AICTE-BATCH1-PERSONALIZED-WORKOUT-DIET-PLANNER-WITH-AI.git
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows:

```bash
.\.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure API Key

Create a `.env` file in the project root and add:

```env
GROQ_API_KEY=your_api_key_here
```

Note:
- Do not upload `.env` to GitHub.
- API keys are stored securely in local environment files.

---

## Run Application

```bash
streamlit run app.py
```

After running, open:

```text
http://localhost:8501
```

---

## Expected Outcome

The system provides:

- Personalized workout schedules
- Customized diet plans
- BMI analysis
- Progress monitoring
- AI-generated fitness recommendations

---

## Author

Gokuldas M

B.Tech Information Technology

Cochin University of Science and Technology (CUSAT)
