import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# SQLite database file path
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")

# connect_args={"check_same_thread": False} is strictly required for SQLite in FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency helper to yield a database session and close it automatically."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
