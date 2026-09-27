import os
import json
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from .database import get_db
from .models import User, WorkoutPlan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def call_gemini_generate_plan(user_data: dict) -> dict:
    """
    Calls Google Gemini API using the modern google-genai SDK to generate
    a comprehensive, structured workout and nutrition plan.
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in .env file. Please add your key to proceed."
        )

    prompt = f"""
    You are FitBuddy AI, a professional sports scientist and certified clinical nutritionist.
    Create a highly personalized 7-Day Workout and Nutrition plan for this user:

    User Profile:
    - Name: {user_data.get('name')}
    - Age: {user_data.get('age')} years
    - Weight: {user_data.get('weight')} kg
    - Height: {user_data.get('height', 'Not provided')} cm
    - Goal: {user_data.get('goal')}
    - Intensity: {user_data.get('intensity')}
    - Dietary Preference: {user_data.get('diet_preference', 'Balanced')}
    - Medical/Injuries: {user_data.get('medical_notes', 'None')}

    Return a valid JSON object matching this schema:
    {{
      "summary": {{
        "daily_calories": 2500,
        "protein_g": 150,
        "carbs_g": 260,
        "fat_g": 65,
        "water_liters": 3.5,
        "coach_note": "Focus on consistency and proper hydration."
      }},
      "workout_plan": {{
        "weekly_overview": "5-Day Push/Pull/Legs split focused on muscle building.",
        "days": [
          {{
            "day": "Monday",
            "focus": "Chest & Triceps",
            "is_rest": false,
            "warmup": "Dynamic arm circles and light pushups",
            "exercises": [
              {{"name": "Bench Press", "sets": 4, "reps": "8-10", "rest": "90s", "tips": "Drive through feet"}}
            ]
          }}
        ]
      }},
      "nutrition_plan": {{
        "diet_type": "High Protein Balanced",
        "meals": [
          {{
            "meal": "Breakfast",
            "items": ["3 eggs omelet", "Oatmeal with almonds"],
            "calories": 550,
            "protein": "32g"
          }}
        ],
        "healthy_swaps": [
          {{"original": "White sugar", "healthy_alternative": "Honey or Stevia", "reason": "Lower glycemic impact"}}
        ]
      }},
      "motivation": "Consistency always defeats motivation."
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API generation failed: {str(e)}")


@router.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    """Render the user input form page (index.html)."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate", response_class=HTMLResponse)
def generate_plan(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    height: float = Form(None),
    gender: str = Form(None),
    goal: str = Form(...),
    intensity: str = Form(...),
    diet_preference: str = Form(None),
    medical_notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle user submission:
    1. Create user in database
    2. Call Gemini AI to generate customized plan
    3. Save plan in database
    4. Render result.html with generated data
    """
    # 1. Create User
    new_user = User(
        name=name,
        age=age,
        weight=weight,
        height=height,
        gender=gender,
        goal=goal,
        intensity=intensity,
        diet_preference=diet_preference,
        medical_notes=medical_notes
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 2. Call Gemini
    plan_data = call_gemini_generate_plan({
        "name": name,
        "age": age,
        "weight": weight,
        "height": height,
        "goal": goal,
        "intensity": intensity,
        "diet_preference": diet_preference,
        "medical_notes": medical_notes
    })

    # 3. Store in WorkoutPlan table
    new_plan = WorkoutPlan(
        user_id=new_user.id,
        goal=goal,
        intensity=intensity,
        original_plan=json.dumps(plan_data),
        updated_plan=None
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "user": new_user,
            "plan_record_id": new_plan.id,
            "plan": plan_data,
            "is_updated": False
        }
    )


@router.get("/plan/{plan_id}", response_class=HTMLResponse)
def view_plan(request: Request, plan_id: int, db: Session = Depends(get_db)):
    """View existing generated plan for a user."""
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Workout Plan not found")

    user = db.query(User).filter(User.id == plan_record.user_id).first()
    active_plan = json.loads(plan_record.updated_plan if plan_record.updated_plan else plan_record.original_plan)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "user": user,
            "plan_record_id": plan_record.id,
            "plan": active_plan,
            "is_updated": bool(plan_record.updated_plan),
            "change_notes": plan_record.change_notes
        }
    )


@router.get("/admin/users", response_class=HTMLResponse)
def admin_all_users(request: Request, db: Session = Depends(get_db)):
    """Admin panel displaying all saved users and their plans (all_users.html)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    plans = db.query(WorkoutPlan).all()
    plans_by_user = {p.user_id: p for p in plans}

    return templates.TemplateResponse(
        "all_users.html",
        {
            "request": request,
            "users": users,
            "plans_by_user": plans_by_user
        }
    )


@router.post("/admin/delete/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user and associated plans."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)
