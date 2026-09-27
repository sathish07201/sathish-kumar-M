from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """
    Users table storing basic user information and fitness goals
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    height = Column(Float, nullable=True)   # in cm
    gender = Column(String(20), nullable=True)
    goal = Column(String(100), nullable=False)  # e.g., Muscle Gain, Weight Loss
    intensity = Column(String(50), nullable=False)  # Low, Medium, High
    diet_preference = Column(String(100), nullable=True)
    medical_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 1-to-many relationship with workout plans
    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', goal='{self.goal}')>"


class WorkoutPlan(Base):
    """
    WorkoutPlan table storing original and AI-updated plans (in JSON text)
    """
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(50), nullable=False)
    original_plan = Column(Text, nullable=False)  # JSON formatted plan
    updated_plan = Column(Text, nullable=True)    # JSON formatted refined plan
    change_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="plans")

    def __repr__(self):
        return f"<WorkoutPlan(id={self.id}, user_id={self.user_id}, goal='{self.goal}')>"
