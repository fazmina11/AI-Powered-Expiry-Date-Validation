"""
tests/conftest.py
Pytest configurations and fixtures for testing FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


# Use a separate test database connection to prevent polluting production data
TEST_DATABASE_URL = "postgresql://expiry_user:expiry_pass@localhost:5432/expiry_db"

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Ensure tables are compiled before tests start."""
    # Ensure the community schema namespace exists
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS community"))
        conn.commit()

    # Import all models to register them on Base.metadata
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db():
    """Yield a function-scoped database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """Yield a FastAPI TestClient configured to override database dependencies."""
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
