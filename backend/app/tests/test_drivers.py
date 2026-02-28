"""
LamiGo Driver API Tests
Unit tests for driver endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDriverEndpoints:
    """Test cases for driver API endpoints."""

    def test_get_all_drivers(self):
        """Test retrieving all drivers."""
        response = client.get("/api/v1/drivers/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_active_drivers(self):
        """Test retrieving only active drivers."""
        response = client.get("/api/v1/drivers/active")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for driver in data:
            assert driver["is_active"] is True

    def test_get_driver_by_id(self):
        """Test retrieving a specific driver by ID."""
        response = client.get("/api/v1/drivers/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data
        assert "phone_number" in data

    def test_get_nonexistent_driver(self):
        """Test retrieving a driver that doesn't exist."""
        response = client.get("/api/v1/drivers/9999")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data


class TestDriverSchema:
    """Test cases for driver data schema validation."""

    def test_driver_has_required_fields(self):
        """Test that driver response includes all required fields."""
        response = client.get("/api/v1/drivers/1")
        data = response.json()
        
        required_fields = ["id", "name", "phone_number", "vehicle_type", "is_active"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_driver_location_fields(self):
        """Test that driver location fields are present."""
        response = client.get("/api/v1/drivers/1")
        data = response.json()
        
        assert "current_location_lat" in data
        assert "current_location_long" in data
