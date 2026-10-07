import json

import httpx
from fastapi.testclient import TestClient

from ticket_app.analysis_models import Request
from ticket_app.analysis_provider import (
    InvalidModelOutput,
    LocalAnalysisProvider,
    ProviderUnavailable,
)
from ticket_app.api import create_app


def make_request():
    return Request(
        subject="API is slow",
        text="The API has high latency and slow responses.",
    )


def make_policy():
    return {
        "id": "g06",
        "categories": [
            "availability",
            "performance",
            "release",
        ],
        "instructions": "Classify the software incident.",
    }


def test_local_provider_valid_json():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "summary": "The API is experiencing high latency.",
                                    "category": "performance",
                                    "priority": "medium",
                                    "next_action": "Ask a reviewer to investigate the API latency.",
                                }
                            )
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    result = provider.analyze(make_request(), make_policy())

    assert result.category == "performance"
    assert result.priority == "medium"


def test_local_provider_invalid_json():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "This is not JSON"
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    try:
        provider.analyze(make_request(), make_policy())
        assert False, "InvalidModelOutput was not raised"
    except InvalidModelOutput:
        pass


def test_local_provider_unavailable():
    def handler(request):
        raise httpx.ConnectError("Connection refused")

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    try:
        provider.analyze(make_request(), make_policy())
        assert False, "ProviderUnavailable was not raised"
    except ProviderUnavailable:
        pass


def test_local_provider_unknown_category():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "summary": "The incident has been analyzed.",
                                    "category": "security",
                                    "priority": "medium",
                                    "next_action": "Ask a reviewer to determine the correct category.",
                                }
                            )
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    result = provider.analyze(make_request(), make_policy())

    assert result.category == "security"
    assert result.category not in make_policy()["categories"]


def test_api_returns_502_for_invalid_model_output(tmp_path):
    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "This is not JSON"
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    client = TestClient(
        create_app(
            provider=provider,
            policy=make_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "API is slow",
            "text": "The API has high latency and slow responses.",
        },
    )

    assert response.status_code == 502


def test_api_returns_503_when_provider_unavailable(tmp_path):
    def handler(request):
        raise httpx.ConnectError("Connection refused")

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    client = TestClient(
        create_app(
            provider=provider,
            policy=make_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "API is slow",
            "text": "The API has high latency and slow responses.",
        },
    )

    assert response.status_code == 503


def test_api_returns_502_for_unknown_category(tmp_path):
    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "summary": "The incident has been analyzed.",
                                    "category": "security",
                                    "priority": "medium",
                                    "next_action": "Ask a reviewer to determine the correct category.",
                                }
                            )
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    client = TestClient(
        create_app(
            provider=provider,
            policy=make_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "API is slow",
            "text": "The API has high latency and slow responses.",
        },
    )

    assert response.status_code == 502


def test_failed_inference_does_not_add_history(tmp_path):
    def handler(request):
        raise httpx.ConnectError("Connection refused")

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://fake",
        model="fake-model",
        transport=transport,
    )

    client = TestClient(
        create_app(
            provider=provider,
            policy=make_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "API is slow",
            "text": "The API has high latency and slow responses.",
        },
    )

    assert response.status_code == 503

    history_response = client.get("/api/history")

    assert history_response.status_code == 200
    assert history_response.json() == []