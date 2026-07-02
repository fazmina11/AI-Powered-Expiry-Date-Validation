"""
Shared test fixtures.

Uses a single in-memory SQLite connection shared across the entire test
so that schema created by create_all is visible to every session.

Key insight: sqlite:///:memory: creates a NEW empty DB per connection.
By keeping ONE connection open for the whole test and binding everything
to it, all sessions see the same tables.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app as fastapi_app
from app.database import Base, get_db

# Force all models onto Base.metadata before create_all
import app.models.product           # noqa: F401
import app.models.inventory         # noqa: F401
import app.models.validation_record # noqa: F401
import app.models.user              # noqa: F401


@pytest.fixture(scope="function")
def client():
    """
    Create a single in-memory SQLite connection, build all tables on it,
    then route every request through a session bound to that same connection.
    After the test, drop all tables and dispose the engine.
    """
    # 1. Engine that always reuses one connection (StaticPool)
    from sqlalchemy.pool import StaticPool
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 2. Create schema on that engine
    Base.metadata.create_all(bind=test_engine)

    # 3. Session factory bound to the test engine
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    # 4. Wire override before TestClient starts
    fastapi_app.dependency_overrides[get_db] = override_get_db

    with TestClient(fastapi_app, raise_server_exceptions=True) as c:
        yield c

    # 5. Teardown
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


# ── Reusable payload helpers ──────────────────────────────────

MILK_PRODUCT = {
    "name": "Milk Packet",
    "sku": "MILK-500ML",
    "barcode": "8901234567890",
    "category": "Dairy",
}

# API version prefix — all routes live under this path
API = "/api/v1"
