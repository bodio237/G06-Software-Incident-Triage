"""Evaluate the six G06 fixtures against the running local API."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


API_URL = os.getenv("API_URL", "http://localhost:8000")
FIXTURES_PATH = Path("../01-group-projects/group-06/fixtures.json")


def call_api(fixture):
    payload = json.dumps(
        {
            "subject": fixture["subject"],
            "text": fixture["text"],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{API_URL}/api/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=75) as response:
            elapsed_ms = round((time.perf_counter() - start) * 1000)
            body = json.load(response)

        return {
            "success": True,
            "elapsed_ms": elapsed_ms,
            "response": body,
        }

    except (urllib.error.URLError, TimeoutError) as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000)

        return {
            "success": False,
            "elapsed_ms": elapsed_ms,
            "error": str(exc),
        }


def main():
    if not FIXTURES_PATH.exists():
        print(f"ERROR: fixtures file not found: {FIXTURES_PATH}")
        sys.exit(1)

    fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))

    if len(fixtures) != 6:
        print(f"ERROR: expected 6 fixtures, found {len(fixtures)}")
        sys.exit(1)

    print("G06 Software Incident Triage - Fixture Evaluation")
    print("=" * 60)
    print(f"API: {API_URL}")
    print(f"Fixtures: {FIXTURES_PATH}")
    print()

    results = []
    failures = 0

    for index, fixture in enumerate(fixtures, start=1):
        print(f"Case {index}/6: {fixture['subject']}")

        result = call_api(fixture)

        if not result["success"]:
            print("  Result: FAILED")
            print(f"  Error: {result['error']}")
            print(f"  Latency: {result['elapsed_ms']} ms")
            print()
            failures += 1

            results.append(
                {
                    "case": index,
                    "subject": fixture["subject"],
                    "expected_category": fixture["expected_category"],
                    "expected_priority": fixture["expected_priority"],
                    "success": False,
                    "latency_ms": result["elapsed_ms"],
                    "error": result["error"],
                }
            )
            continue

        response = result["response"]
        analysis = response.get("analysis", {})

        actual_category = analysis.get("category")
        actual_priority = analysis.get("priority")

        valid_response = all(
            key in analysis
            for key in ["summary", "category", "priority", "next_action"]
        )

        category_match = actual_category == fixture["expected_category"]
        priority_match = actual_priority == fixture["expected_priority"]
        review_required = response.get("requires_review") is True

        case_ok = (
            valid_response
            and category_match
            and priority_match
            and review_required
        )

        print(f"  Expected category: {fixture['expected_category']}")
        print(f"  Actual category:   {actual_category}")
        print(f"  Expected priority: {fixture['expected_priority']}")
        print(f"  Actual priority:   {actual_priority}")
        print(f"  Latency:           {result['elapsed_ms']} ms")
        print(f"  Valid response:    {valid_response}")
        print(f"  Review required:   {review_required}")
        print(f"  Result:            {'PASS' if case_ok else 'FAIL'}")
        print()

        if not case_ok:
            failures += 1

        results.append(
            {
                "case": index,
                "subject": fixture["subject"],
                "expected_category": fixture["expected_category"],
                "actual_category": actual_category,
                "category_match": category_match,
                "expected_priority": fixture["expected_priority"],
                "actual_priority": actual_priority,
                "priority_match": priority_match,
                "valid_response": valid_response,
                "requires_review": review_required,
                "success": True,
                "latency_ms": result["elapsed_ms"],
            }
        )

    successful = sum(
        1 for result in results if result["success"]
    )

    category_matches = sum(
        1 for result in results
        if result.get("category_match") is True
    )

    priority_matches = sum(
        1 for result in results
        if result.get("priority_match") is True
    )

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Fixtures evaluated:       {len(results)}/6")
    print(f"Successful API calls:     {successful}/6")
    print(f"Category agreement:       {category_matches}/6")
    print(f"Priority agreement:       {priority_matches}/6")

    successful_latencies = [
        result["latency_ms"]
        for result in results
        if result["success"]
    ]

    if successful_latencies:
        average_latency = round(
            sum(successful_latencies) / len(successful_latencies)
        )
        print(f"Average latency:          {average_latency} ms")

    print(f"Failures/mismatches:      {failures}")

    if failures:
        print("\nEvaluation FAILED.")
        sys.exit(1)

    print("\nEvaluation PASSED.")


if __name__ == "__main__":
    main()