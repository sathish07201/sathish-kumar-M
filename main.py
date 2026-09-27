from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routes import router as main_router
from .updated_plan import router as update_router

# Automatically create all database tables in fitbuddy.db if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FitBuddy - AI Workout & Nutrition Generator",
    description="Full-stack AI personal fitness & nutrition platform built with FastAPI, SQLite, and Google Gemini API.",
    version="1.0.0"
)

# Mount static folder for CSS styling
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include feature routers
app.include_router(main_router)
app.include_router(update_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
