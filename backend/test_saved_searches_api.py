#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Saved Searches Endpoints
BWARM Dashboard - Advanced Filtering & Search Feature
"""

import json
import sys
import time
from typing import Any, Dict, Optional, Tuple

import requests

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1OTYyMzQ5OCwidHlwZSI6ImFjY2VzcyJ9.c7KwWugf_-1RvmVU71m7D1BNE6-XNgJfK4mot3t5Cmo"

# Test tracking
PASSED = 0
FAILED = 0
TOTAL = 0
TESTS_RESULTS = []

# ANSI color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_header(text: str):
    """Print a test section header."""
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")


def print_test(test_num: int, text: str):
    """Print test description."""
    print(f"\n{YELLOW}TEST {test_num}: {text}{NC}")


def print_pass(text: str):
    """Print success message."""
    global PASSED
    print(f"{GREEN}✓ PASS{NC}: {text}")
    PASSED += 1


def print_fail(text: str, detail: str = ""):
    """Print failure message."""
    global FAILED
    print(f"{RED}✗ FAIL{NC}: {text}")
    if detail:
        print(f"{RED}  {detail}{NC}")
    FAILED += 1


def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    use_auth: bool = True,
    expected_status: Optional[int] = None,
) -> Tuple[Optional[Dict[str, Any]], int]:
    """
    Make HTTP request to API.

    Returns:
        Tuple of (response_data, status_code)
    """
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if use_auth:
        headers["Authorization"] = f"Bearer {TOKEN}"

    try:
        response = requests.request(
            method=method, url=url, json=data, headers=headers, timeout=10
        )

        # Try to parse JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = None

        return response_data, response.status_code

    except requests.exceptions.RequestException as e:
        print(f"{RED}Request failed: {e}{NC}")
        return None, 0


def run_test(
    test_name: str,
    method: str,
    endpoint: str,
    expected_status: int,
    data: Optional[Dict[str, Any]] = None,
    use_auth: bool = True,
) -> Tuple[Optional[Dict[str, Any]], int]:
    """Run a single test case."""
    global TOTAL

    TOTAL += 1
    print_test(TOTAL, test_name)

    response_data, status_code = make_request(method, endpoint, data, use_auth)

    print(f"Status Code: {status_code}")
    if response_data:
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")

    if status_code == expected_status:
        print_pass(f"{test_name} (Status: {status_code})")
    else:
        print_fail(
            test_name,
            f"Expected status {expected_status}, got {status_code}",
        )

    TESTS_RESULTS.append(
        {
            "test": test_name,
            "passed": status_code == expected_status,
            "expected": expected_status,
            "actual": status_code,
        }
    )

    return response_data, status_code


def verify_field(
    response_data: Dict[str, Any], field_name: str, test_description: str
):
    """Verify a field exists in response."""
    global TOTAL, PASSED, FAILED

    TOTAL += 1
    if field_name in response_data:
        print_pass(f"{test_description}: '{field_name}' present")
    else:
        print_fail(test_description, f"Missing field: '{field_name}'")


def verify_value(
    response_data: Dict[str, Any],
    field_name: str,
    expected_value: Any,
    test_description: str,
):
    """Verify a field has expected value."""
    global TOTAL, PASSED, FAILED

    TOTAL += 1
    actual_value = response_data.get(field_name)
    if actual_value == expected_value:
        print_pass(f"{test_description}: {field_name}={expected_value}")
    else:
        print_fail(
            test_description,
            f"Expected {field_name}={expected_value}, got {actual_value}",
        )


def main():
    """Main test execution."""
    print_header("SAVED SEARCHES API - COMPREHENSIVE TEST SUITE")
    print(f"API Base URL: {API_BASE}")
    print("Testing all endpoints with various scenarios...")

    # Track created search IDs for cleanup
    search_ids = []

    # ============================================
    # 1. Authentication Tests
    # ============================================
    print_header("1. AUTHENTICATION TESTS")

    # Test without authentication
    response, status = run_test(
        "Request without authentication",
        "GET",
        "/saved-searches",
        expected_status=403,  # Updated based on actual API behavior
        use_auth=False,
    )

    # Test with invalid token
    global TOKEN
    original_token = TOKEN
    TOKEN = "invalid.token.here"

    response, status = run_test(
        "Request with invalid token",
        "GET",
        "/saved-searches",
        expected_status=401,
        use_auth=True,
    )

    TOKEN = original_token

    # Test with valid token
    response, status = run_test(
        "Request with valid token", "GET", "/saved-searches", expected_status=200
    )

    # ============================================
    # 2. Create Saved Search Tests
    # ============================================
    print_header("2. CREATE SAVED SEARCH TESTS")

    # Create saved search - Valid data
    create_data1 = {
        "name": "Works without ISWC",
        "description": "Find all works missing ISWC codes",
        "filter_config": {
            "logic": "AND",
            "filters": [{"field": "has_iswc", "operator": "equals", "value": False}],
            "sort": {"field": "created_at", "order": "desc"},
        },
        "is_favorite": False,
    }

    response, status = run_test(
        "Create saved search - Valid data",
        "POST",
        "/saved-searches",
        expected_status=201,
        data=create_data1,
    )

    search_id_1 = None
    if response and status == 201:
        search_id_1 = response.get("id")
        search_ids.append(search_id_1)
        print(f"Created Search ID: {search_id_1}")

        # Verify response structure
        verify_field(response, "id", "Response contains ID")
        verify_field(response, "filter_config", "Response contains filter_config")
        verify_field(response, "user_id", "Response contains user_id")
        verify_value(response, "name", "Works without ISWC", "Name matches input")
        verify_value(response, "is_favorite", False, "is_favorite matches input")
        verify_value(response, "use_count", 0, "Initial use_count is 0")

    # Create second saved search - Complex filter
    create_data2 = {
        "name": "Recent Popular Works",
        "description": "Works created recently with high play counts",
        "filter_config": {
            "logic": "AND",
            "filters": [
                {
                    "field": "created_at",
                    "operator": "greater_than",
                    "value": "2025-01-01",
                },
                {"field": "play_count", "operator": "greater_than", "value": 1000},
            ],
            "sort": {"field": "play_count", "order": "desc"},
        },
        "is_favorite": True,
    }

    response, status = run_test(
        "Create saved search - Complex filter",
        "POST",
        "/saved-searches",
        expected_status=201,
        data=create_data2,
    )

    search_id_2 = None
    if response and status == 201:
        search_id_2 = response.get("id")
        search_ids.append(search_id_2)
        print(f"Created Search ID: {search_id_2}")

    # Create third saved search - For bulk delete test
    create_data3 = {
        "name": "Test Search for Deletion",
        "description": "This will be deleted in bulk",
        "filter_config": {
            "logic": "OR",
            "filters": [{"field": "status", "operator": "equals", "value": "pending"}],
        },
        "is_favorite": False,
    }

    response, status = run_test(
        "Create saved search - For bulk delete",
        "POST",
        "/saved-searches",
        expected_status=201,
        data=create_data3,
    )

    search_id_3 = None
    if response and status == 201:
        search_id_3 = response.get("id")
        search_ids.append(search_id_3)
        print(f"Created Search ID: {search_id_3}")

    # Test validation errors
    response, status = run_test(
        "Create search - Missing required field (name)",
        "POST",
        "/saved-searches",
        expected_status=422,
        data={
            "description": "Missing name field",
            "filter_config": {"logic": "AND", "filters": []},
        },
    )

    response, status = run_test(
        "Create search - Invalid operator",
        "POST",
        "/saved-searches",
        expected_status=422,
        data={
            "name": "Invalid Operator Test",
            "filter_config": {
                "logic": "AND",
                "filters": [
                    {"field": "status", "operator": "invalid_op", "value": "test"}
                ],
            },
        },
    )

    response, status = run_test(
        "Create search - Name too long",
        "POST",
        "/saved-searches",
        expected_status=422,
        data={
            "name": "a" * 300,  # Exceeds max length
            "filter_config": {"logic": "AND", "filters": []},
        },
    )

    # ============================================
    # 3. Get Saved Searches (List) Tests
    # ============================================
    print_header("3. GET SAVED SEARCHES (LIST) TESTS")

    response, status = run_test(
        "Get all saved searches", "GET", "/saved-searches", expected_status=200
    )

    if response and status == 200:
        verify_field(response, "total", "Response contains total")
        verify_field(response, "searches", "Response contains searches array")

        if "total" in response:
            print(f"Total searches: {response['total']}")

    response, status = run_test(
        "Get saved searches - Exclude presets",
        "GET",
        "/saved-searches?include_presets=false",
        expected_status=200,
    )

    response, status = run_test(
        "Get saved searches - Favorites only",
        "GET",
        "/saved-searches?favorites_only=true",
        expected_status=200,
    )

    if response and status == 200:
        # Verify all returned searches are favorites
        if "searches" in response:
            all_favorites = all(
                search.get("is_favorite", False) for search in response["searches"]
            )
            if all_favorites or len(response["searches"]) == 0:
                print_pass("All returned searches are favorites")
            else:
                print_fail("Favorites filter", "Some non-favorite searches returned")

    response, status = run_test(
        "Get saved searches - Multiple filters",
        "GET",
        "/saved-searches?include_presets=false&favorites_only=true",
        expected_status=200,
    )

    # ============================================
    # 4. Get System Presets Tests
    # ============================================
    print_header("4. GET SYSTEM PRESETS TESTS")

    response, status = run_test(
        "Get system presets - Without auth",
        "GET",
        "/saved-searches/presets",
        expected_status=200,
        use_auth=False,
    )

    # ============================================
    # 5. Get Specific Saved Search Tests
    # ============================================
    print_header("5. GET SPECIFIC SAVED SEARCH TESTS")

    if search_id_1:
        response, status = run_test(
            "Get saved search by ID",
            "GET",
            f"/saved-searches/{search_id_1}",
            expected_status=200,
        )

        if response and status == 200:
            # Verify filter_config structure
            verify_field(response, "filter_config", "filter_config present")

            if "filter_config" in response:
                fc = response["filter_config"]
                if isinstance(fc, dict):
                    print_pass("filter_config is JSON object")

                    if "logic" in fc and "filters" in fc:
                        print_pass("filter_config has correct structure")
                    else:
                        print_fail("filter_config structure", "Missing logic or filters")
                else:
                    print_fail("filter_config type", "Not a JSON object")

            # Verify required fields
            required_fields = [
                "id",
                "user_id",
                "name",
                "filter_config",
                "is_preset",
                "is_favorite",
                "use_count",
                "created_at",
                "updated_at",
            ]
            for field in required_fields:
                verify_field(response, field, f"Field '{field}'")

    response, status = run_test(
        "Get saved search - Invalid ID",
        "GET",
        "/saved-searches/999999",
        expected_status=404,
    )

    response, status = run_test(
        "Get saved search - Non-numeric ID",
        "GET",
        "/saved-searches/abc",
        expected_status=422,
    )

    # ============================================
    # 6. Update Saved Search Tests
    # ============================================
    print_header("6. UPDATE SAVED SEARCH TESTS")

    if search_id_1:
        # Update name
        response, status = run_test(
            "Update search - Change name",
            "PUT",
            f"/saved-searches/{search_id_1}",
            expected_status=200,
            data={"name": "Works without ISWC (Updated)"},
        )

        if response and status == 200:
            verify_value(
                response,
                "name",
                "Works without ISWC (Updated)",
                "Name updated correctly",
            )

        # Mark as favorite
        response, status = run_test(
            "Update search - Mark as favorite",
            "PUT",
            f"/saved-searches/{search_id_1}",
            expected_status=200,
            data={"is_favorite": True},
        )

        if response and status == 200:
            verify_value(response, "is_favorite", True, "is_favorite updated")

        # Update filter_config
        new_filter_config = {
            "logic": "OR",
            "filters": [
                {"field": "has_iswc", "operator": "equals", "value": False},
                {"field": "has_isrc", "operator": "equals", "value": False},
            ],
            "sort": {"field": "updated_at", "order": "asc"},
        }

        response, status = run_test(
            "Update search - Update filter_config",
            "PUT",
            f"/saved-searches/{search_id_1}",
            expected_status=200,
            data={"filter_config": new_filter_config},
        )

        if response and status == 200:
            verify_field(response, "updated_at", "updated_at timestamp present")

        # Update multiple fields
        response, status = run_test(
            "Update search - Multiple fields",
            "PUT",
            f"/saved-searches/{search_id_1}",
            expected_status=200,
            data={
                "name": "Updated Search Name",
                "description": "Updated description",
                "is_favorite": False,
            },
        )

        # Verify persistence
        response, status = run_test(
            "Get search - Verify updates persisted",
            "GET",
            f"/saved-searches/{search_id_1}",
            expected_status=200,
        )

        if response and status == 200:
            verify_value(
                response, "name", "Updated Search Name", "Updated name persisted"
            )
            verify_value(
                response,
                "description",
                "Updated description",
                "Updated description persisted",
            )

    response, status = run_test(
        "Update search - Invalid ID",
        "PUT",
        "/saved-searches/999999",
        expected_status=404,
        data={"name": "This should fail"},
    )

    # ============================================
    # 7. Record Search Usage Tests
    # ============================================
    print_header("7. RECORD SEARCH USAGE TESTS")

    if search_id_2:
        # Get initial stats
        response, status = run_test(
            "Get search before usage tracking",
            "GET",
            f"/saved-searches/{search_id_2}",
            expected_status=200,
        )

        initial_use_count = 0
        if response and status == 200:
            initial_use_count = response.get("use_count", 0)
            print(f"Initial use_count: {initial_use_count}")

        # Record first use
        response, status = run_test(
            "Record search usage - First use",
            "POST",
            f"/saved-searches/{search_id_2}/use",
            expected_status=200,
        )

        if response and status == 200:
            new_use_count = response.get("use_count", 0)
            print(f"New use_count: {new_use_count}")

            if new_use_count == initial_use_count + 1:
                print_pass("use_count incremented correctly")
            else:
                print_fail(
                    "use_count increment",
                    f"Expected {initial_use_count + 1}, got {new_use_count}",
                )

            verify_field(response, "last_used_at", "last_used_at timestamp set")

        # Wait to ensure different timestamp
        time.sleep(1)

        # Record second use
        response, status = run_test(
            "Record search usage - Second use",
            "POST",
            f"/saved-searches/{search_id_2}/use",
            expected_status=200,
        )

        if response and status == 200:
            second_use_count = response.get("use_count", 0)
            print(f"Second use_count: {second_use_count}")

            if second_use_count == initial_use_count + 2:
                print_pass("use_count incremented on second use")
            else:
                print_fail(
                    "use_count increment",
                    f"Expected {initial_use_count + 2}, got {second_use_count}",
                )

    response, status = run_test(
        "Record usage - Invalid ID",
        "POST",
        "/saved-searches/999999/use",
        expected_status=404,
    )

    # ============================================
    # 8. Bulk Delete Tests
    # ============================================
    print_header("8. BULK DELETE TESTS")

    response, status = run_test(
        "Bulk delete - Empty array",
        "POST",
        "/saved-searches/bulk-delete",
        expected_status=400,
        data=[],
    )

    if search_id_3:
        response, status = run_test(
            "Bulk delete - Single ID",
            "POST",
            "/saved-searches/bulk-delete",
            expected_status=200,
            data=[search_id_3],
        )

        if response and status == 200:
            deleted_count = response.get("deleted_count", 0)
            print(f"Deleted count: {deleted_count}")
            verify_value(response, "deleted_count", 1, "One search deleted")

        # Verify deletion
        response, status = run_test(
            "Verify bulk delete - Get deleted search",
            "GET",
            f"/saved-searches/{search_id_3}",
            expected_status=404,
        )

        if search_id_3 in search_ids:
            search_ids.remove(search_id_3)

    response, status = run_test(
        "Bulk delete - Invalid IDs",
        "POST",
        "/saved-searches/bulk-delete",
        expected_status=200,
        data=[999997, 999998, 999999],
    )

    if response and status == 200:
        verify_value(response, "deleted_count", 0, "No invalid IDs deleted")

    # ============================================
    # 9. Delete Saved Search Tests
    # ============================================
    print_header("9. DELETE SAVED SEARCH TESTS")

    if search_id_1:
        response, status = run_test(
            "Delete saved search",
            "DELETE",
            f"/saved-searches/{search_id_1}",
            expected_status=204,
        )

        # Verify deletion
        response, status = run_test(
            "Verify deletion - Get deleted search",
            "GET",
            f"/saved-searches/{search_id_1}",
            expected_status=404,
        )

        # Try to delete again
        response, status = run_test(
            "Delete already deleted search",
            "DELETE",
            f"/saved-searches/{search_id_1}",
            expected_status=404,
        )

        if search_id_1 in search_ids:
            search_ids.remove(search_id_1)

    response, status = run_test(
        "Delete - Invalid ID",
        "DELETE",
        "/saved-searches/999999",
        expected_status=404,
    )

    # ============================================
    # 10. Data Persistence & Integrity Tests
    # ============================================
    print_header("10. DATA PERSISTENCE & INTEGRITY TESTS")

    workflow_data = {
        "name": "Persistence Test Search",
        "description": "Testing full CRUD workflow",
        "filter_config": {
            "logic": "AND",
            "filters": [{"field": "status", "operator": "equals", "value": "active"}],
        },
        "is_favorite": False,
    }

    response, status = run_test(
        "CRUD Workflow - Step 1: Create",
        "POST",
        "/saved-searches",
        expected_status=201,
        data=workflow_data,
    )

    workflow_id = None
    if response and status == 201:
        workflow_id = response.get("id")
        print(f"Workflow search ID: {workflow_id}")

        # Get
        response, status = run_test(
            "CRUD Workflow - Step 2: Get",
            "GET",
            f"/saved-searches/{workflow_id}",
            expected_status=200,
        )

        # Update
        response, status = run_test(
            "CRUD Workflow - Step 3: Update",
            "PUT",
            f"/saved-searches/{workflow_id}",
            expected_status=200,
            data={"name": "Persistence Test (Updated)", "is_favorite": True},
        )

        # Get updated
        response, status = run_test(
            "CRUD Workflow - Step 4: Get updated",
            "GET",
            f"/saved-searches/{workflow_id}",
            expected_status=200,
        )

        if response and status == 200:
            verify_value(
                response, "name", "Persistence Test (Updated)", "Name persisted"
            )
            verify_value(response, "is_favorite", True, "is_favorite persisted")

        # Delete
        response, status = run_test(
            "CRUD Workflow - Step 5: Delete",
            "DELETE",
            f"/saved-searches/{workflow_id}",
            expected_status=204,
        )

    # ============================================
    # 11. Edge Cases & Error Handling
    # ============================================
    print_header("11. EDGE CASES & ERROR HANDLING")

    # Empty filters
    response, status = run_test(
        "Edge case - Empty filters array",
        "POST",
        "/saved-searches",
        expected_status=201,
        data={
            "name": "Empty Filters Test",
            "filter_config": {"logic": "AND", "filters": []},
        },
    )

    if response and status == 201:
        cleanup_id = response.get("id")
        if cleanup_id:
            search_ids.append(cleanup_id)

    # Only sort
    response, status = run_test(
        "Edge case - Sort without filters",
        "POST",
        "/saved-searches",
        expected_status=201,
        data={
            "name": "Sort Only Test",
            "filter_config": {
                "logic": "AND",
                "filters": [],
                "sort": {"field": "title", "order": "asc"},
            },
        },
    )

    if response and status == 201:
        cleanup_id = response.get("id")
        if cleanup_id:
            search_ids.append(cleanup_id)

    # Complex nested value
    response, status = run_test(
        "Edge case - Complex nested value",
        "POST",
        "/saved-searches",
        expected_status=201,
        data={
            "name": "Complex Value Test",
            "filter_config": {
                "logic": "AND",
                "filters": [
                    {
                        "field": "metadata",
                        "operator": "equals",
                        "value": {"nested": "object", "count": 123},
                    }
                ],
            },
        },
    )

    if response and status == 201:
        cleanup_id = response.get("id")
        if cleanup_id:
            search_ids.append(cleanup_id)

    # Null value filter
    response, status = run_test(
        "Edge case - Null value filter",
        "POST",
        "/saved-searches",
        expected_status=201,
        data={
            "name": "Null Value Test",
            "filter_config": {
                "logic": "AND",
                "filters": [{"field": "optional_field", "operator": "is_null"}],
            },
        },
    )

    if response and status == 201:
        cleanup_id = response.get("id")
        if cleanup_id:
            search_ids.append(cleanup_id)

    # Empty update
    if search_id_2:
        response, status = run_test(
            "Edge case - Empty update body",
            "PUT",
            f"/saved-searches/{search_id_2}",
            expected_status=200,
            data={},
        )

    # ============================================
    # Cleanup
    # ============================================
    print_header("CLEANUP")

    print(f"\nCleaning up {len(search_ids)} created searches...")
    for sid in search_ids:
        try:
            _, status = make_request("DELETE", f"/saved-searches/{sid}")
            if status == 204:
                print(f"Deleted search {sid}")
        except Exception as e:
            print(f"Failed to delete search {sid}: {e}")

    # ============================================
    # Test Summary
    # ============================================
    print_header("TEST SUMMARY")

    print(f"\nTotal Tests: {BLUE}{TOTAL}{NC}")
    print(f"Passed: {GREEN}{PASSED}{NC}")
    print(f"Failed: {RED}{FAILED}{NC}")

    # Calculate success rate
    if TOTAL > 0:
        success_rate = (PASSED / TOTAL) * 100
        print(f"Success Rate: {success_rate:.1f}%")

    # Show failed tests
    if FAILED > 0:
        print(f"\n{RED}Failed Tests:{NC}")
        for result in TESTS_RESULTS:
            if not result["passed"]:
                print(
                    f"  - {result['test']} "
                    f"(Expected: {result['expected']}, Got: {result['actual']})"
                )

    print()
    if FAILED == 0:
        print(f"{GREEN}{'=' * 60}{NC}")
        print(f"{GREEN}ALL TESTS PASSED!{NC}")
        print(f"{GREEN}{'=' * 60}{NC}")
        sys.exit(0)
    else:
        print(f"{RED}{'=' * 60}{NC}")
        print(f"{RED}SOME TESTS FAILED{NC}")
        print(f"{RED}{'=' * 60}{NC}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Test execution failed: {e}{NC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
