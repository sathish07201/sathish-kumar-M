#!/usr/bin/env python3
"""
FitBuddy Launcher Script
Starts Uvicorn server with hot-reload enabled.
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ Starting FitBuddy AI Workout & Nutrition Platform...")
    print("👉 Web App:  http://127.0.0.1:8000")
    print("👉 Admin:    http://127.0.0.1:8000/admin/users")
    print("👉 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
