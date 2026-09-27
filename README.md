# FitBuddy — AI-Powered Workout & Nutrition Generator 🏋️‍♂️

A production-ready academic/capstone project that generates personalized 7-day workout routines and nutrition meal plans using **FastAPI**, **SQLite**, **SQLAlchemy**, and **Google Gemini AI**.

---

## 🏗️ Project Architecture & Tech Stack

- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Backend:** Python 3.9+ with FastAPI
- **AI Model:** Google Gemini 3.8 Flash via modern `google-genai` SDK
- **Database:** SQLite3 (`fitbuddy.db`)
- **ORM:** SQLAlchemy 2.0+
- **Server:** Uvicorn ASGI Server

---

## 📁 Project Folder Structure

```
FitBuddy/
│
├── app/
│   ├── main.py            # FastAPI entry point, mounts routes & static files
│   ├── database.py        # SQLAlchemy SQLite engine & session dependency
│   ├── models.py          # User & WorkoutPlan database models
│   ├── routes.py          # Primary routes (Home form, Gemini API, Admin)
│   └── updated_plan.py    # AI plan refinement / update logic
│
├── templates/
│   ├── index.html         # User metrics intake form
│   ├── result.html        # AI-generated workout & nutrition planner
│   └── all_users.html     # Admin dashboard showing all registered users
│
├── static/
│   └── style.css          # Modern dark-mode styling
│
├── .env                   # Environment variable storing GEMINI_API_KEY
├── requirements.txt       # Python package dependencies
├── run.py                 # Quick launcher script
└── README.md              # Documentation
```

---

## 🚀 Setup & Execution Guide (Step-by-Step)

### 1. Extract or Clone Project
Open the `FitBuddy` folder in **VS Code**.

### 2. Create Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key
Create a `.env` file in the root directory:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_from_google_ai_studio
DATABASE_URL=sqlite:///./fitbuddy.db
```
*(Get free key from [Google AI Studio](https://aistudio.google.com/))*

### 5. Run the Server
```bash
python run.py
```
*Or using uvicorn directly:*
```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Open in Browser
- **User App:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Admin Dashboard:** [http://127.0.0.1:8000/admin/users](http://127.0.0.1:8000/admin/users)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
