import json
from pathlib import Path

from fastapi.testclient import TestClient

from ticket_app.api import create_app
from ticket_app.analysis_provider import MockAnalysisProvider


def create_test_client(tmp_path):
    policy = json.loads(Path("scenarios/g00.json").read_text())

    return TestClient(
        create_app(
            provider=MockAnalysisProvider(),
            policy=policy,
            db_path=str(tmp_path / "test.db"),
        )
    )


def test_baseline_health_and_analysis(tmp_path):
    client = create_test_client(tmp_path)

    assert client.get("/health").status_code == 200

    response = client.post(
        "/api/analyze",
        json={
            "subject": "Help request",
            "text": "Please help me route this request.",
        },
    )

    assert response.status_code == 200
    assert response.json()["requires_review"] is True


def test_invalid_input(tmp_path):
    client = create_test_client(tmp_path)

    response = client.post(
        "/api/analyze",
        json={
            "subject": "x",
            "text": "x",
        },
    )

    assert response.status_code == 422


def test_subject_too_long(tmp_path):
    client = create_test_client(tmp_path)

    response = client.post(
        "/api/analyze",
        json={
            "subject": "A" * 101,
            "text": "This is a valid request text.",
        },
    )

    assert response.status_code == 422


def test_text_too_long(tmp_path):
    client = create_test_client(tmp_path)

    response = client.post(
        "/api/analyze",
        json={
            "subject": "Valid subject",
            "text": "A" * 4001,
        },
    )

    assert response.status_code == 422


def test_extra_fields_are_rejected(tmp_path):
    client = create_test_client(tmp_path)

    response = client.post(
        "/api/analyze",
        json={
            "subject": "Valid subject",
            "text": "This is a valid request text.",
            "unexpected": "not allowed",
        },
    )

    assert response.status_code == 422