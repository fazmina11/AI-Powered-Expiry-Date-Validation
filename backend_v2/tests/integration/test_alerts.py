"""
tests/integration/test_alerts.py
Integration tests for Community Safety Alert Engine (CSAE) routes.
"""
import pytest
from fastapi.testclient import TestClient


def test_list_safety_alerts_success(client: TestClient):
    """Verify listing safety alerts returns the standardized success envelope wrapper."""
    response = client.get("/api/v1/community/alerts")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_alerts_dashboard(client: TestClient):
    """Verify safety alerts dashboard endpoint returns the correct envelope and keys."""
    response = client.get("/api/v1/community/alerts/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    dash = data["data"]
    assert "total_alerts" in dash
    assert "active_alerts" in dash
    assert "average_resolution_time" in dash
