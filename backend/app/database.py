"""
database.py — SQLAlchemy engine, session factory, declarative base, and
              the FastAPI get_db dependency.

All other modules import Base from here so every model is registered
on the same metadata object.

Note: Base.metadata.create_all() is called at startup by main.py in
development mode only. For production, use Alembic migrations:
    alembic upgrade head
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# SQLite needs check_same_thread=False; PostgreSQL does not need it.
_connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    The session is always closed after the request, even on errors.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
