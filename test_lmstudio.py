import time
import urllib.request
import json

payload = {
    "model": "google/gemma-4-e4b",
    "messages": [
        {
            "role": "user",
            "content": "Return only the word OK"
        }
    ],
    "temperature": 0
}

data = json.dumps(payload).encode("utf-8")

request = urllib.request.Request(
    "http://localhost:1234/v1/chat/completions",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

start = time.perf_counter()

with urllib.request.urlopen(request, timeout=90) as response:
    result = response.read().decode("utf-8")

elapsed = time.perf_counter() - start

print("STATUS:", response.status)
print("TIME:", round(elapsed, 2), "seconds")
print(result[:500])