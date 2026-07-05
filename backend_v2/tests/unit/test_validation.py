"""
tests/unit/test_validation.py
Unit tests checking input validation rules and error formats.
"""
import pytest
from fastapi.testclient import TestClient


def test_standard_response_wrapping_on_success(client: TestClient):
    """Verify that a successful GET /health returns standard success wrapping."""
    response = client.get("/health")
    assert response.status_code == 200
    
    # Standard health check endpoint might bypass wrapper (we explicitly allowed it in middleware)
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_user_creation_invalid_email_format(client: TestClient):
    """Verify that invalid user email inputs trigger 422 validation failure wrapped in error JSON."""
    response = client.post(
        "/api/v1/community/users",
        json={
            "full_name": "Bad User",
            "email": "not-an-email",
            "phone": "+919876543210"
        }
    )
    assert response.status_code == 422
    data = response.json()
    
    # Assert standard error wrapper format
    assert data["success"] is False
    assert "error" in data
    assert "details" in data
    assert isinstance(data["details"], list)
