# FitAI Planner

Personalized Workout & Diet Planner powered by Google Gemini AI.

## Setup

1. Create a Python virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your Gemini API key:

- Copy `.env.example` to `.env` or edit the existing `.env` file and set:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the app with Streamlit:

```powershell
streamlit run app.py
```

5. Open the browser at the local URL shown by Streamlit (usually `http://localhost:8501`).

## Notes

- The app uses Google Gemini via the `google-generativeai` package. Provide a valid `GEMINI_API_KEY` to enable AI features.
- Profile data and logs are stored in a local SQLite database at `data/fitai.db`.
- If you want me to run the app locally and verify plan generation, tell me and I will start it in the terminal.
