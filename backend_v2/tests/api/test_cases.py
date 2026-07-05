"""
tests/api/test_cases.py
API tests for Investigation & Case Management Engine (ICME) routes.
"""
import pytest
from fastapi.testclient import TestClient


def test_list_investigation_cases(client: TestClient):
    """Verify that query for cases returns the standardized response envelope."""
    response = client.get("/api/v1/community/cases")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_cases_dashboard(client: TestClient):
    """Verify case dashboard endpoint outputs correct structured indicators."""
    response = client.get("/api/v1/community/cases/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    dash = data["data"]
    assert "total_cases" in dash
    assert "open_cases" in dash
    assert "cases_by_priority" in dash
    assert "cases_by_status" in dash
