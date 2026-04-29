import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database import get_db
from app.models import User
from app.utils import hash_password

client = TestClient(app)


def make_mock_db():
    return MagicMock()


class TestSearchEndpoint:

    def test_search_missing_location(self):
        response = client.post("/api/stores/search", json={})
        assert response.status_code == 400

    def test_search_with_coordinates(self):
        with patch("app.routers.stores.check_rate_limit", return_value=True):
            with patch("app.services.search_stores", return_value=[]):
                response = client.post("/api/stores/search", json={
                    "latitude": 42.3601,
                    "longitude": -71.0589,
                    "radius_miles": 10
                })
                assert response.status_code == 200
                assert "results" in response.json()

    def test_rate_limit_exceeded(self):
        with patch("app.routers.stores.check_rate_limit", return_value=False):
            response = client.post("/api/stores/search", json={
                "latitude": 42.3601,
                "longitude": -71.0589
            })
            assert response.status_code == 429


class TestAuthEndpoint:

    def test_login_invalid_credentials(self):
        response = client.post("/api/auth/login", json={
            "email": "wrong@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_success(self):
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "AdminTest123!"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()