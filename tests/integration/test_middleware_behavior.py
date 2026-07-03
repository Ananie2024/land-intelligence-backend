# tests/integration/test_middleware_behavior.py

"""
Integration tests for response middleware behavior.

Verifies that StandardizeResponseMiddleware and PaginationMiddleware:
- Correctly handle paginated results
- Pass through file downloads unchanged
- Pass through error responses unchanged
- Do not consume the response body in a way that crashes the server
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.testclient import TestClient

from app.api.middleware.response_middleware import (
    StandardizeResponseMiddleware,
    PaginationMiddleware,
)
from app.api.middleware.exception_handler import register_exception_handler


# ---------------------------------------------------------------------------
# Helpers to build minimal apps for isolated testing
# ---------------------------------------------------------------------------


def build_app():
    application = FastAPI()
    register_exception_handler(application)
    application.add_middleware(StandardizeResponseMiddleware)
    application.add_middleware(PaginationMiddleware)
    return application


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app = build_app()
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Error responses — must be standardized via CentralizedExceptionMiddleware
# ---------------------------------------------------------------------------


def test_error_response_is_standardized(client):
    @client.app.get("/error")
    def _error():
        raise HTTPException(status_code=400, detail="bad request")

    response = client.get("/error")
    assert response.status_code == 400
    body = response.json()
    # CentralizedExceptionMiddleware catches HTTPExceptions and returns standardized format
    assert body["success"] is False
    assert "errors" in body
    assert body["message"] == "bad request"


# ---------------------------------------------------------------------------
# 2. Successful non-JSON — must NOT be consumed or transformed
# ---------------------------------------------------------------------------


def test_plain_text_not_standardized(client):
    @client.app.get("/text")
    def _text():
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse("hello world")

    response = client.get("/text")
    assert response.status_code == 200
    assert response.text == "hello world"


# ---------------------------------------------------------------------------
# 3. Successful JSON — must be standardized
# ---------------------------------------------------------------------------


def test_json_standardized(client):
    @client.app.get("/json")
    def _json():
        return {"key": "value"}

    response = client.get("/json")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {"key": "value"}
    assert "timestamp" in body


# ---------------------------------------------------------------------------
# 4. File downloads — must NOT consume body or raise content-length issues
# ---------------------------------------------------------------------------


def test_file_response_passthrough(tmp_path, client):
    # Write a tiny dummy file
    dummy = tmp_path / "dummy.txt"
    dummy.write_text("file content")

    @client.app.get("/download")
    def _download():
        return FileResponse(
            path=str(dummy),
            media_type="text/plain",
            filename="dummy.txt",
        )

    response = client.get("/download")
    assert response.status_code == 200
    assert response.content == b"file content"


# ---------------------------------------------------------------------------
# 5. Paginated-like JSON — wrapped into standardized response
# ---------------------------------------------------------------------------


def test_paginated_json_standardized(client):
    @client.app.get("/paginated")
    def _paginated():
        return {
            "items": [{"id": 1}, {"id": 2}],
            "total": 2,
            "page": 1,
            "size": 20,
            "pages": 1,
            "extra": "value",
        }

    response = client.get("/paginated")
    assert response.status_code == 200
    body = response.json()
    # StandardizeResponseMiddleware runs first and wraps the payload;
    # with the original paginated dict as data, PaginationMiddleware
    # no longer sees the top-level pagination keys, so behavior here is
    # just the standard wrapper with the original object preserved in data.
    assert body["success"] is True
    assert body["data"]["items"] == [{"id": 1}, {"id": 2}]
    assert body["data"]["total"] == 2


# ---------------------------------------------------------------------------
# 6. Streaming-like generator response — must not crash after inspection
# ---------------------------------------------------------------------------


def test_streaming_response_success(client):
    async def stream():
        yield b'{"result": "ok"}'

    @client.app.get("/stream")
    async def _stream():
        from starlette.responses import StreamingResponse

        return StreamingResponse(stream(), media_type="application/json")

    response = client.get("/stream")
    assert response.status_code == 200
    body = response.json()
    # Streaming JSON responses get standardized too
    assert body["success"] is True
    assert body["data"] == {"result": "ok"}
