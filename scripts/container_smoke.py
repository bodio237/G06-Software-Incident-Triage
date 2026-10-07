"""Smoke-test a Docker image in mock mode."""

import json
import subprocess
import sys
import time
from uuid import uuid4


def run(command):
    return subprocess.run(command, check=True)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/container_smoke.py IMAGE")
        sys.exit(2)

    image = sys.argv[1]
    name = "ci-smoke-" + uuid4().hex[:12]

    try:
        run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                name,
                "-e",
                "LLM_PROVIDER=mock",
                "-e",
                "SCENARIO_ID=g06",
                "-e",
                "DB_PATH=/data/analyses.db",
                image,
            ]
        )

        for _ in range(30):
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    name,
                    "python",
                    "-c",
                    (
                        "import urllib.request; "
                        "urllib.request.urlopen("
                        "'http://localhost:8000/health', "
                        "timeout=5"
                        ")"
                    ),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                break

            time.sleep(1)
        else:
            raise RuntimeError("API health check failed")

        payload = json.dumps(
            {
                "subject": "Service unavailable",
                "text": (
                    "The service is currently unavailable "
                    "and needs to be reviewed."
                ),
            }
        )

        code = (
            "import json, urllib.request; "
            "payload = json.loads(" + repr(payload) + "); "
            "request = urllib.request.Request("
            "'http://localhost:8000/api/analyze', "
            "data=json.dumps(payload).encode(), "
            "headers={'Content-Type': 'application/json'}, "
            "method='POST'"
            "); "
            "response = urllib.request.urlopen(request, timeout=10); "
            "data = json.load(response); "
            "assert data['scenario'] == 'g06'; "
            "assert data['provider'] == 'mock'; "
            "assert data['requires_review'] is True; "
            "assert data['analysis']['category'] == 'availability'; "
            "print(json.dumps(data))"
        )

        run(
            [
                "docker",
                "exec",
                name,
                "python",
                "-c",
                code,
            ]
        )

        print("Container smoke test passed.")

    finally:
        subprocess.run(
            [
                "docker",
                "rm",
                "-f",
                name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    main()