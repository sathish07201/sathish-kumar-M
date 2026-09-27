# FitBuddy — Project Viva Q&A & Academic Report 🎓

## 1. Project Title
**FitBuddy: AI-Powered Personalized Fitness & Nutrition Generation Platform**

---

## 2. Abstract / Synopsis
Personalized fitness coaching is often expensive and inaccessible to everyday individuals. **FitBuddy** solves this by leveraging generative artificial intelligence (Google Gemini 3.8 Flash) integrated into a fast, lightweight web architecture (FastAPI and SQLite). The system accepts anthropometric data (age, weight, height) alongside fitness objectives, intensity levels, and dietary preferences to synthesize an adaptive 7-day workout routine and macro-nutrient split. The system persists user records in a relational database, supports real-time plan refinement, and offers an administrator dashboard for data auditing.

---

## 3. Top Viva Questions & Answers

### Q1: Why did you choose FastAPI over Flask or Django?
**Answer:**
1. **Asynchronous performance:** FastAPI is built on Starlette and Pydantic, making it one of the fastest Python web frameworks available.
2. **Built-in Swagger Docs:** Automatic interactive API documentation generated at `/docs`.
3. **Data validation:** Native Pydantic type hinting catches bad data before processing.
4. **Lightweight:** Unlike Django, FastAPI does not impose heavy overhead when working with microservices and SQLite.

### Q2: How does the Gemini AI integration work?
**Answer:**
We use Google's modern `google-genai` SDK. When the user submits their metrics, the backend crafts a domain-engineered prompt and requests a structured JSON response schema. This guarantees that Gemini returns strictly typed JSON with day-by-day exercises, sets, reps, rest intervals, and macronutrient targets.

### Q3: Explain the Database Schema & Relationships.
**Answer:**
We have two primary tables connected via a 1-to-Many foreign key relationship:
1. `users` table: `id` (Primary Key), `name`, `age`, `weight`, `height`, `goal`, `intensity`, `created_at`.
2. `workout_plans` table: `id` (Primary Key), `user_id` (Foreign Key referencing `users.id`), `goal`, `intensity`, `original_plan` (JSON), `updated_plan` (JSON), `change_notes`.

### Q4: How is the "Update Plan" feature implemented?
**Answer:**
In `app/updated_plan.py`, the user submits a modification prompt (e.g., "I hurt my shoulder, give me leg exercises only"). The backend retrieves the current plan from SQLite, sends both the context and modification request to Gemini, and stores the newly synthesized version in the `updated_plan` column while preserving the historical `original_plan`.
