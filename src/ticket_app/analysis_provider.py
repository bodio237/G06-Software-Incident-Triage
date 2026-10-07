from typing import Protocol
import json
import httpx

from ticket_app.analysis_models import Analysis, Request


class ProviderUnavailable(RuntimeError):
    pass


class InvalidModelOutput(RuntimeError):
    pass


class AnalysisProvider(Protocol):
    def analyze(self, request: Request, policy: dict) -> Analysis:
        ...


class MockAnalysisProvider:
    def analyze(self, request: Request, policy: dict) -> Analysis:
        return Analysis(
            summary=f"{request.subject}: {request.text}"[:240],
            category=policy["categories"][0],
            priority="medium",
            next_action="Ask a reviewer to route the request.",
        )


class LocalAnalysisProvider:
    def __init__(
        self,
        base_url,
        model,
        timeout=60,
        max_tokens=300,
        key="",
        transport=None,
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.key = key
        self.transport = transport

    def analyze(self, request: Request, policy: dict) -> Analysis:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"{policy['instructions']}\n\n"
                        "Return ONLY a JSON object with exactly these keys: "
                        "summary, category, priority, next_action.\n"
                        f"category must be one of: {', '.join(policy['categories'])}.\n"
                        "priority must be one of: low, medium, high.\n"
                        "Do not use Markdown or code fences."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Subject: {request.subject}\n"
                        f"Request: {request.text}"
                    ),
                },
            ],
            "temperature": 0,
            "max_tokens": self.max_tokens,
        }

        headers = {}

        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"

        try:
            if self.transport is not None:
                with httpx.Client(
                    transport=self.transport,
                    timeout=self.timeout,
                ) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                    )
            else:
                response = httpx.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )

            response.raise_for_status()

        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            raise ProviderUnavailable(
                "Local model inference is unavailable"
            ) from exc

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)

            return Analysis.model_validate(result)

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise InvalidModelOutput(
                "The local model returned invalid JSON output"
            ) from exc