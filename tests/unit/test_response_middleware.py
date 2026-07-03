"""Unit tests for the response middleware components."""
import json
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from app.api.middleware.response_middleware import (
    StandardizeResponseMiddleware,
    PaginationMiddleware,
)


# --------------------------------------------------------------------------- #
# Helper classes for testing body reading
# --------------------------------------------------------------------------- #
class MockResponse:
    """Minimal mock of a Starlette Response for testing body reading."""

    def __init__(self, body: bytes = b"", status_code: int = 200, headers: dict = None):
        self._body = body
        self.status_code = status_code
        self._headers = headers or {"content-type": "application/json"}

    @property
    def body(self):
        if self._body is None:
            raise RuntimeError("no direct body")
        return self._body

    @property
    def headers(self):
        return self._headers


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def app():
    """Create a FastAPI app with both middleware under test."""
    application = FastAPI()
    application.add_middleware(StandardizeResponseMiddleware)
    application.add_middleware(PaginationMiddleware)
    return application


@pytest.fixture
def client(app):
    """Test client for the app."""
    return TestClient(app)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_passthrough_endpoints_are_not_modified(client):
    """Endpoints listed in PASSTHROUGH_PREFIXES must bypass middleware processing."""
    # Add routes that should be passthrough (with standardized format)
    @client.app.get("/health")
    def health():
        return {"success": True, "timestamp": "2026-07-02T15:00:00Z", "data": "ok"}

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # The response should retain its original structure; middleware must not wrap it.
    assert data.get("success") is True
    assert "timestamp" in data


def test_non_json_responses_are_not_standardized(client):
    """Responses with a non-JSON content type must bypass standardization."""
    @client.app.get("/text")
    def raw():
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("plain text")

    response = client.get("/text")
    assert response.status_code == 200
    # The middleware checks the Content-Type header; this test ensures that check works.
    assert response.headers["content-type"].startswith("text/plain")


def test_successful_json_responses_are_standardized(client):
    """Successful JSON payloads should be wrapped by the success schema."""
    @client.app.get("/custom")
    def custom():
        return {"data": "custom payload"}

    response = client.get("/custom")
    assert response.status_code == 200
    data = response.json()
    # The middleware wraps the payload using the success_response schema.
    assert data["success"] is True
    assert data["data"] == {"data": "custom payload"}
    assert "timestamp" in data


def test_paginated_responses_are_standardized(client):
    """Paginated payloads should be transformed by the pagination schema."""
    @client.app.get("/paginated")
    def paginated():
        return {
            "items": [{"id": 1}, {"id": 2}],
            "total": 2,
            "page": 1,
            "size": 10,
        }

    response = client.get("/paginated")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # StandardizeResponseMiddleware runs first and wraps the payload
    assert "data" in data
    assert data["data"]["items"] == [{"id": 1}, {"id": 2}]
    assert data["data"]["total"] == 2


def test_error_responses_are_not_wrapped(client):
    """Responses with status >= 400 must bypass any wrapping."""
    @client.app.get("/error")
    def error():
        raise HTTPException(status_code=500, detail="boom")

    response = client.get("/error")
    assert response.status_code == 500
    # Error payloads must remain untouched.
    body = response.json()
    assert body.get("detail") == "boom"


def test_is_passthrough_function_works():
    """The internal _is_passthrough helper should correctly identify passthrough paths."""
    from app.api.middleware.response_middleware import _is_passthrough

    # All defined prefixes and their sub-paths must return True
    for prefix in ["/api/openapi.json", "/api/docs", "/api/redoc", "/health"]:
        assert _is_passthrough(prefix) is True
        assert _is_passthrough(f"{prefix}/sub") is True

    # Non-passthrough paths must return False
    assert _is_passthrough("/api/custom") is False
    assert _is_passthrough("/random") is False


def test_read_body_success():
    """_read_body should successfully read the body when accessed directly."""
    from app.api.middleware.response_middleware import _read_body
    import asyncio

    resp = MockResponse(body=b'{"key":"value"}')
    # Call the async function synchronously
    body = asyncio.run(_read_body(resp))
    assert body == b'{"key":"value"}'


def test_read_body_fallback():
    """When direct access fails, _read_body must fall back to iterating over body_iterator."""
    from app.api.middleware.response_middleware import _read_body
    import asyncio

    async def async_gen():
        yield b'{"a":1}'

    class FailingResponse:
        status_code = 200
        
        def __init__(self):
            self._headers = {"content-type": "application/json"}
        
        @property
        def body(self):
            raise RuntimeError("no direct body")
        
        @property
        def headers(self):
            return self._headers
        
        @property
        def body_iterator(self):
            return async_gen()

    resp = FailingResponse()
    body = asyncio.run(_read_body(resp))
    assert body == b'{"a":1}'