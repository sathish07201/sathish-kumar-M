import os
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from .database import get_db
from .models import User, WorkoutPlan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


@router.post("/update-plan/{plan_id}", response_class=HTMLResponse)
def update_existing_plan(
    request: Request,
    plan_id: int,
    user_modification: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Refines an existing plan based on user feedback (e.g. 'I want home workouts'
    or 'Replace chicken with vegetarian protein'). Calls Gemini AI and saves into updated_plan column.
    """
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found")

    user = db.query(User).filter(User.id == plan_record.user_id).first()
    current_plan = json.loads(plan_record.updated_plan if plan_record.updated_plan else plan_record.original_plan)

    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured.")

    prompt = f"""
    You are FitBuddy AI. An existing workout & nutrition plan was generated for user {user.name}.
    The user has submitted this modification request:

    "{user_modification}"

    Existing Plan Summary:
    {json.dumps(current_plan.get('summary', {}), indent=2)}

    Please adapt and return the UPDATED plan in valid JSON adhering to the exact same schema.
    Ensure all user modification requests are seamlessly implemented.
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
        updated_data = json.loads(response.text)

        # Update in database
        plan_record.updated_plan = json.dumps(updated_data)
        plan_record.change_notes = user_modification
        plan_record.updated_at = datetime.utcnow()
        db.commit()

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "user": user,
                "plan_record_id": plan_record.id,
                "plan": updated_data,
                "is_updated": True,
                "change_notes": user_modification
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan refinement failed: {str(e)}")
