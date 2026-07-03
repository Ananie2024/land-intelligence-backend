# tests/unit/test_exception_handler.py

"""
Unit tests for centralized exception handler.
Tests that all exceptions are caught and standardized properly when used with the 
full middleware stack (as verified in integration tests).
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api.middleware.exception_handler import register_exception_handler
from app.api.middleware.response_middleware import StandardizeResponseMiddleware


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def app():
    """Create a FastAPI app with centralized exception handler and response middleware."""
    application = FastAPI()
    register_exception_handler(application)
    application.add_middleware(StandardizeResponseMiddleware)
    return application


@pytest.fixture
def client(app):
    """Test client for the app."""
    return TestClient(app)


# --------------------------------------------------------------------------- #
# Test: HTTP Exception handling
# --------------------------------------------------------------------------- #

def test_http_exception_returns_standardized_response(client):
    """HTTPException should return standardized error format."""
    @client.app.get("/not_found")
    def not_found():
        raise HTTPException(status_code=404, detail="Resource not found")

    response = client.get("/not_found")
    assert response.status_code == 404
    data = response.json()
    # Should use standardized error format
    assert data["success"] is False
    assert "errors" in data
    assert data["message"] == "Resource not found"


def test_http_exception_401_returns_www_authenticate_header(client):
    """401 HTTPException should include WWW-Authenticate header."""
    @client.app.get("/unauthorized")
    def unauthorized():
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = client.get("/unauthorized")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_http_exception_403_returns_standardized_response(client):
    """403 HTTPException should return standardized error format."""
    @client.app.get("/forbidden")
    def forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")

    response = client.get("/forbidden")
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Forbidden"


def test_http_exception_409_returns_standardized_response(client):
    """409 HTTPException should return standardized error format."""
    @client.app.get("/conflict")
    def conflict():
        raise HTTPException(status_code=409, detail="Conflict")

    response = client.get("/conflict")
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Conflict"


# --------------------------------------------------------------------------- #
# Test: Request Validation Error handling (422)
# --------------------------------------------------------------------------- #

def test_request_validation_error_returns_standardized_response(client):
    """RequestValidationError should return standardized 422 response."""
    class TestModel(BaseModel):
        name: str
        age: int

    @client.app.post("/validate")
    def validate_endpoint(data: TestModel):
        return {"received": data}

    response = client.post("/validate", json={"name": "test", "age": "not_a_number"})
    assert response.status_code == 422
    data = response.json()
    # Should use standardized error format
    assert data["success"] is False
    assert "errors" in data


# --------------------------------------------------------------------------- #
# Test: Successful response handling
# --------------------------------------------------------------------------- #

def test_successful_response_is_standardized(client):
    """Successful responses should be standardized."""
    @client.app.get("/success")
    def success():
        return {"data": "test value"}

    response = client.get("/success")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == {"data": "test value"}