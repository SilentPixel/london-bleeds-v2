# Database engine and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

def get_engine():
    """Create and return SQLAlchemy engine for SQLite"""
    return create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that yields a database session and closes it on finally"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
