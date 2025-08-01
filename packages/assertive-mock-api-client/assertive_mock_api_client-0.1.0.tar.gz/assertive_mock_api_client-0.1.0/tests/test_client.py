import pytest
from unittest.mock import patch, create_autospec
import json
from assertive import is_gte, is_eq, was_called_once_with, has_key_values
from assertive.serialize import serialize
from assertive_mock_api_client import MockApiClient
import httpx


@pytest.fixture
def mock_http_client():
    mock_instance = create_autospec(httpx.Client)

    with patch("httpx.Client") as MockClientClass:
        MockClientClass.return_value = mock_instance
        yield mock_instance


def test_basic_request_call(mock_http_client):
    """Test the basic functionality of confirm_request with minimal parameters"""

    mock_client = MockApiClient(base_url="http://localhost:8910")

    mock_http_client.post.return_value = create_autospec(httpx.Response)

    mock_client.when_requested_with(path="/test", method="GET").respond_with_json(
        status_code=200, body={"hello": "world"}
    )

    assert mock_http_client.post == was_called_once_with(
        "/__mock__/stubs",
        json={
            "request": {
                "path": "/test",
                "method": "GET",
            },
            "action": {
                "response": {
                    "status_code": 200,
                    "body": json.dumps({"hello": "world"}),
                    "headers": {"Content-Type": "application/json"},
                }
            },
        },
    )


def test_confirm_request(mock_http_client):
    """Test the basic functionality of confirm_request with minimal parameters"""

    mock_client = MockApiClient(base_url="http://localhost:8910")

    mock_http_client.post.return_value = create_autospec(httpx.Response)

    mock_client.confirm_request(
        path="/test",
        method=is_eq("GET") | is_eq("POST"),
        headers={"Accept": "application/json"},
        query=has_key_values({"id": is_gte(1)}),
    )

    assert mock_http_client.post == was_called_once_with(
        "/__mock__/assert",
        json={
            "path": "/test",
            "method": serialize(is_eq("GET") | is_eq("POST")),
            "headers": {"Accept": "application/json"},
            "query": serialize(has_key_values({"id": is_gte(1)})),
            "times": serialize(is_gte(1)),
        },
    )
