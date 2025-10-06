#!/usr/bin/env python3
"""Simple script to get a valid JWT token for testing."""

import requests
import sys

API_BASE = "http://localhost:8000/api/v1"

try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "admin@example.com", "password": "admin123"},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(token)
        sys.exit(0)
    else:
        print(f"Error: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
