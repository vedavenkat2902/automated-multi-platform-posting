
from unittest.mock import AsyncMock
import pytest

from app.main import posting_service
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_valid_message():

    response = client.post(
        "/posting",
        json={
            "message": "Check our platform https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "success" in data
    assert "results" in data
    assert len(data["results"]) == 5


def test_message_without_url():

    response = client.post(
        "/posting",
        json={
            "message": "Check our latest platform"
        }
    )

    assert response.status_code == 422


def test_message_with_multiple_urls():

    response = client.post(
        "/posting",
        json={
            "message": "Visit https://google.com and https://example.com"
        }
    )

    assert response.status_code == 422


def test_message_exceeding_200_characters():

    response = client.post(
        "/posting",
        json={
            "message": (
                "A" * 190 + " https://example.com"
            )
        }
    )

    assert response.status_code == 422


def test_invalid_url():

    response = client.post(
        "/posting",
        json={
            "message": "Check our platform https://"
        }
    )

    assert response.status_code == 422


def test_all_platforms_fail_independently(monkeypatch):

    for platform in posting_service.platforms:
        monkeypatch.setattr(
            platform,
            "publish",
            AsyncMock(side_effect=Exception("API unavailable"))
        )

    response = client.post(
        "/posting",
        json={
            "message": "Check our platform https://example.com"
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert len(data["results"]) == 5

    for result in data["results"]:
        assert result["status"] == "failed"
        assert result["error"] is not None


def test_one_platform_succeeds_others_fail(monkeypatch):

    successful_result = {
        "platform": "WordPress",
        "status": "success",
        "posted_url": "https://example.wordpress.com/sample-post",
        "public_access": True,
        "date": "2026-11-20",
        "time": "10:30:00",
        "error": None
    }

    for index, platform in enumerate(posting_service.platforms):

        if index == 0:
            monkeypatch.setattr(
                platform,
                "publish",
                AsyncMock(return_value=successful_result)
            )
        else:
            monkeypatch.setattr(
                platform,
                "publish",
                AsyncMock(side_effect=Exception("API unavailable"))
            )

    response = client.post(
        "/posting",
        json={
            "message": "Check our platform https://example.com"
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["results"]) == 5

    assert data["results"][0]["status"] == "success"

    for result in data["results"][1:]:
        assert result["status"] == "failed"


def test_all_five_platforms_are_called(monkeypatch):

    mock_publish = AsyncMock(
        side_effect=Exception("API unavailable")
    )

    for platform in posting_service.platforms:
        monkeypatch.setattr(
            platform,
            "publish",
            mock_publish
        )

    response = client.post(
        "/posting",
        json={
            "message": "Check our platform https://example.com"
        }
    )

    assert response.status_code == 200
    assert mock_publish.await_count == 5


def test_empty_message():

    response = client.post(
        "/posting",
        json={
            "message": ""
        }
    )

    assert response.status_code == 422


def test_response_contains_required_fields():

    response = client.post(
        "/posting",
        json={
            "message": "Check our platform https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["success"], bool)
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 5

    required_fields = {
        "platform",
        "status",
        "posted_url",
        "public_access",
        "date",
        "time",
        "error"
    }

    for result in data["results"]:
        assert required_fields.issubset(result.keys())
