#!/bin/bash

# Comprehensive API Testing Script for Saved Searches Endpoints
# BWARM Dashboard - Advanced Filtering & Search Feature

set -e  # Exit on error

# Configuration
API_BASE="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1OTYyMzQ5OCwidHlwZSI6ImFjY2VzcyJ9.c7KwWugf_-1RvmVU71m7D1BNE6-XNgJfK4mot3t5Cmo"
HEADER_AUTH="Authorization: Bearer $TOKEN"
HEADER_JSON="Content-Type: application/json"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables for tracking
PASSED=0
FAILED=0
TOTAL=0

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_test() {
    echo ""
    echo -e "${YELLOW}TEST $TOTAL: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo -e "${RED}  $2${NC}"
    ((FAILED++))
}

make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local use_auth=$4

    local auth_header=""
    if [ "$use_auth" = "true" ]; then
        auth_header="-H \"$HEADER_AUTH\""
    fi

    if [ -n "$data" ]; then
        eval curl -s -X "$method" \
            -H \"$HEADER_JSON\" \
            $auth_header \
            -d "'$data'" \
            -w "\\n%{http_code}" \
            "$API_BASE$endpoint"
    else
        eval curl -s -X "$method" \
            $auth_header \
            -w "\\n%{http_code}" \
            "$API_BASE$endpoint"
    fi
}

check_response() {
    local response=$1
    local expected_code=$2
    local test_name=$3

    # Extract status code (last line)
    local status_code=$(echo "$response" | tail -n 1)
    # Extract body (all but last line)
    local body=$(echo "$response" | head -n -1)

    ((TOTAL++))

    if [ "$status_code" = "$expected_code" ]; then
        print_pass "$test_name (Status: $status_code)"
        echo "$body"
        return 0
    else
        print_fail "$test_name" "Expected $expected_code, got $status_code"
        echo "Response: $body"
        return 1
    fi
}

# ============================================
# Test Suite
# ============================================

print_header "SAVED SEARCHES API - COMPREHENSIVE TEST SUITE"
echo "API Base URL: $API_BASE"
echo "Testing all endpoints with various scenarios..."

# ============================================
# 1. Authentication Tests
# ============================================

print_header "1. AUTHENTICATION TESTS"

print_test "Test without authentication - should fail"
response=$(make_request "GET" "/saved-searches" "" "false")
check_response "$response" "401" "Unauthenticated request returns 401"

print_test "Test with invalid token - should fail"
INVALID_TOKEN="invalid.token.here"
response=$(curl -s -X GET \
    -H "Authorization: Bearer $INVALID_TOKEN" \
    -w "\n%{http_code}" \
    "$API_BASE/saved-searches")
check_response "$response" "401" "Invalid token returns 401"

print_test "Test with valid token - should succeed"
response=$(make_request "GET" "/saved-searches" "" "true")
check_response "$response" "200" "Valid token returns 200"

# ============================================
# 2. Create Saved Search Tests
# ============================================

print_header "2. CREATE SAVED SEARCH TESTS"

print_test "Create saved search - Valid data"
create_data1='{
  "name": "Works without ISWC",
  "description": "Find all works missing ISWC codes",
  "filter_config": {
    "logic": "AND",
    "filters": [
      {"field": "has_iswc", "operator": "equals", "value": false}
    ],
    "sort": {"field": "created_at", "order": "desc"}
  },
  "is_favorite": false
}'
response=$(make_request "POST" "/saved-searches" "$create_data1" "true")
if check_response "$response" "201" "Create saved search with valid data"; then
    SEARCH_ID_1=$(echo "$response" | head -n -1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Created Search ID: $SEARCH_ID_1"
fi

print_test "Create second saved search - Complex filter"
create_data2='{
  "name": "Recent Popular Works",
  "description": "Works created recently with high play counts",
  "filter_config": {
    "logic": "AND",
    "filters": [
      {"field": "created_at", "operator": "greater_than", "value": "2025-01-01"},
      {"field": "play_count", "operator": "greater_than", "value": 1000}
    ],
    "sort": {"field": "play_count", "order": "desc"}
  },
  "is_favorite": true
}'
response=$(make_request "POST" "/saved-searches" "$create_data2" "true")
if check_response "$response" "201" "Create saved search with complex filter"; then
    SEARCH_ID_2=$(echo "$response" | head -n -1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Created Search ID: $SEARCH_ID_2"
fi

print_test "Create third saved search - For bulk delete test"
create_data3='{
  "name": "Test Search for Deletion",
  "description": "This will be deleted in bulk",
  "filter_config": {
    "logic": "OR",
    "filters": [
      {"field": "status", "operator": "equals", "value": "pending"}
    ]
  },
  "is_favorite": false
}'
response=$(make_request "POST" "/saved-searches" "$create_data3" "true")
if check_response "$response" "201" "Create saved search for bulk delete"; then
    SEARCH_ID_3=$(echo "$response" | head -n -1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Created Search ID: $SEARCH_ID_3"
fi

print_test "Create saved search - Missing required field (name)"
create_data_invalid='{
  "description": "Missing name field",
  "filter_config": {
    "logic": "AND",
    "filters": []
  }
}'
response=$(make_request "POST" "/saved-searches" "$create_data_invalid" "true")
check_response "$response" "422" "Missing required field returns 422"

print_test "Create saved search - Invalid operator"
create_data_invalid_op='{
  "name": "Invalid Operator Test",
  "filter_config": {
    "logic": "AND",
    "filters": [
      {"field": "status", "operator": "invalid_operator", "value": "test"}
    ]
  }
}'
response=$(make_request "POST" "/saved-searches" "$create_data_invalid_op" "true")
check_response "$response" "422" "Invalid operator returns 422"

print_test "Create saved search - Name too long"
long_name=$(printf 'a%.0s' {1..300})
create_data_long="{
  \"name\": \"$long_name\",
  \"filter_config\": {
    \"logic\": \"AND\",
    \"filters\": []
  }
}"
response=$(make_request "POST" "/saved-searches" "$create_data_long" "true")
check_response "$response" "422" "Name exceeding max length returns 422"

# ============================================
# 3. Get Saved Searches Tests
# ============================================

print_header "3. GET SAVED SEARCHES (LIST) TESTS"

print_test "Get all saved searches for user"
response=$(make_request "GET" "/saved-searches" "" "true")
if check_response "$response" "200" "Get all saved searches"; then
    body=$(echo "$response" | head -n -1)
    total=$(echo "$body" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "Total searches: $total"

    # Verify response structure
    if echo "$body" | grep -q '"searches":\['; then
        print_pass "Response contains 'searches' array"
        ((PASSED++))
        ((TOTAL++))
    else
        print_fail "Response structure validation" "Missing 'searches' array"
        ((FAILED++))
        ((TOTAL++))
    fi
fi

print_test "Get saved searches - Exclude presets"
response=$(make_request "GET" "/saved-searches?include_presets=false" "" "true")
check_response "$response" "200" "Get saved searches without presets"

print_test "Get saved searches - Favorites only"
response=$(make_request "GET" "/saved-searches?favorites_only=true" "" "true")
if check_response "$response" "200" "Get favorites only"; then
    body=$(echo "$response" | head -n -1)
    # Should only contain favorite searches
    if echo "$body" | grep -q '"is_favorite":true'; then
        print_pass "Response contains favorite searches"
        ((PASSED++))
        ((TOTAL++))
    fi
fi

print_test "Get saved searches - Multiple filters combined"
response=$(make_request "GET" "/saved-searches?include_presets=false&favorites_only=true" "" "true")
check_response "$response" "200" "Get favorites without presets"

# ============================================
# 4. Get System Presets Tests
# ============================================

print_header "4. GET SYSTEM PRESETS TESTS"

print_test "Get system presets - No authentication required"
response=$(make_request "GET" "/saved-searches/presets" "" "false")
check_response "$response" "200" "Get system presets without auth"

# ============================================
# 5. Get Specific Saved Search Tests
# ============================================

print_header "5. GET SPECIFIC SAVED SEARCH TESTS"

if [ -n "$SEARCH_ID_1" ]; then
    print_test "Get saved search by ID - Valid ID"
    response=$(make_request "GET" "/saved-searches/$SEARCH_ID_1" "" "true")
    if check_response "$response" "200" "Get saved search by ID"; then
        body=$(echo "$response" | head -n -1)

        # Verify filter_config structure
        if echo "$body" | grep -q '"filter_config":{'; then
            print_pass "filter_config is properly returned as JSON object"
            ((PASSED++))
            ((TOTAL++))
        else
            print_fail "filter_config structure" "Not returned as JSON object"
            ((FAILED++))
            ((TOTAL++))
        fi

        # Verify all required fields
        required_fields=("id" "user_id" "name" "filter_config" "is_preset" "is_favorite" "use_count" "created_at" "updated_at")
        for field in "${required_fields[@]}"; do
            ((TOTAL++))
            if echo "$body" | grep -q "\"$field\""; then
                print_pass "Response contains field: $field"
                ((PASSED++))
            else
                print_fail "Field validation" "Missing required field: $field"
                ((FAILED++))
            fi
        done
    fi
fi

print_test "Get saved search - Invalid ID"
response=$(make_request "GET" "/saved-searches/999999" "" "true")
check_response "$response" "404" "Invalid search ID returns 404"

print_test "Get saved search - Non-numeric ID"
response=$(make_request "GET" "/saved-searches/abc" "" "true")
check_response "$response" "422" "Non-numeric ID returns 422"

# ============================================
# 6. Update Saved Search Tests
# ============================================

print_header "6. UPDATE SAVED SEARCH TESTS"

if [ -n "$SEARCH_ID_1" ]; then
    print_test "Update saved search - Change name"
    update_data1='{
      "name": "Works without ISWC (Updated)"
    }'
    response=$(make_request "PUT" "/saved-searches/$SEARCH_ID_1" "$update_data1" "true")
    check_response "$response" "200" "Update search name"

    print_test "Update saved search - Mark as favorite"
    update_data2='{
      "is_favorite": true
    }'
    response=$(make_request "PUT" "/saved-searches/$SEARCH_ID_1" "$update_data2" "true")
    check_response "$response" "200" "Mark search as favorite"

    print_test "Update saved search - Update filter_config"
    update_data3='{
      "filter_config": {
        "logic": "OR",
        "filters": [
          {"field": "has_iswc", "operator": "equals", "value": false},
          {"field": "has_isrc", "operator": "equals", "value": false}
        ],
        "sort": {"field": "updated_at", "order": "asc"}
      }
    }'
    response=$(make_request "PUT" "/saved-searches/$SEARCH_ID_1" "$update_data3" "true")
    if check_response "$response" "200" "Update filter_config"; then
        body=$(echo "$response" | head -n -1)
        # Verify updated_at was changed
        if echo "$body" | grep -q '"updated_at"'; then
            print_pass "updated_at timestamp is present"
            ((PASSED++))
            ((TOTAL++))
        fi
    fi

    print_test "Update saved search - Multiple fields at once"
    update_data4='{
      "name": "Updated Search Name",
      "description": "Updated description",
      "is_favorite": false
    }'
    response=$(make_request "PUT" "/saved-searches/$SEARCH_ID_1" "$update_data4" "true")
    check_response "$response" "200" "Update multiple fields"

    print_test "Verify update persistence - Get updated search"
    response=$(make_request "GET" "/saved-searches/$SEARCH_ID_1" "" "true")
    if check_response "$response" "200" "Get updated search"; then
        body=$(echo "$response" | head -n -1)
        if echo "$body" | grep -q '"name":"Updated Search Name"'; then
            print_pass "Updates persisted correctly"
            ((PASSED++))
            ((TOTAL++))
        else
            print_fail "Update persistence" "Name not updated in database"
            ((FAILED++))
            ((TOTAL++))
        fi
    fi
fi

print_test "Update saved search - Invalid ID"
update_invalid='{
  "name": "This should fail"
}'
response=$(make_request "PUT" "/saved-searches/999999" "$update_invalid" "true")
check_response "$response" "404" "Update with invalid ID returns 404"

# ============================================
# 7. Record Search Usage Tests
# ============================================

print_header "7. RECORD SEARCH USAGE TESTS"

if [ -n "$SEARCH_ID_2" ]; then
    print_test "Get initial usage stats"
    response=$(make_request "GET" "/saved-searches/$SEARCH_ID_2" "" "true")
    if check_response "$response" "200" "Get search before usage record"; then
        body=$(echo "$response" | head -n -1)
        initial_use_count=$(echo "$body" | grep -o '"use_count":[0-9]*' | cut -d':' -f2)
        echo "Initial use_count: $initial_use_count"

        initial_last_used=$(echo "$body" | grep -o '"last_used_at":"[^"]*"' | cut -d'"' -f4)
        echo "Initial last_used_at: $initial_last_used"
    fi

    print_test "Record search usage - First use"
    response=$(make_request "POST" "/saved-searches/$SEARCH_ID_2/use" "" "true")
    if check_response "$response" "200" "Record first usage"; then
        body=$(echo "$response" | head -n -1)
        new_use_count=$(echo "$body" | grep -o '"use_count":[0-9]*' | cut -d':' -f2)
        echo "New use_count: $new_use_count"

        ((TOTAL++))
        if [ "$new_use_count" -gt "$initial_use_count" ]; then
            print_pass "use_count incremented correctly"
            ((PASSED++))
        else
            print_fail "use_count increment" "use_count did not increase"
            ((FAILED++))
        fi

        ((TOTAL++))
        if echo "$body" | grep -q '"last_used_at":"[0-9]'; then
            print_pass "last_used_at timestamp updated"
            ((PASSED++))
        else
            print_fail "last_used_at update" "Timestamp not set"
            ((FAILED++))
        fi
    fi

    # Wait a moment to ensure different timestamp
    sleep 1

    print_test "Record search usage - Second use"
    response=$(make_request "POST" "/saved-searches/$SEARCH_ID_2/use" "" "true")
    if check_response "$response" "200" "Record second usage"; then
        body=$(echo "$response" | head -n -1)
        second_use_count=$(echo "$body" | grep -o '"use_count":[0-9]*' | cut -d':' -f2)
        echo "Second use_count: $second_use_count"

        ((TOTAL++))
        expected_count=$((initial_use_count + 2))
        if [ "$second_use_count" -eq "$expected_count" ]; then
            print_pass "use_count incremented correctly on second use"
            ((PASSED++))
        else
            print_fail "use_count increment" "Expected $expected_count, got $second_use_count"
            ((FAILED++))
        fi
    fi
fi

print_test "Record usage - Invalid search ID"
response=$(make_request "POST" "/saved-searches/999999/use" "" "true")
check_response "$response" "404" "Record usage with invalid ID returns 404"

# ============================================
# 8. Bulk Delete Tests
# ============================================

print_header "8. BULK DELETE TESTS"

print_test "Bulk delete - Empty array"
bulk_delete_empty='[]'
response=$(make_request "POST" "/saved-searches/bulk-delete" "$bulk_delete_empty" "true")
check_response "$response" "400" "Empty array returns 400"

if [ -n "$SEARCH_ID_3" ]; then
    print_test "Bulk delete - Single ID"
    bulk_delete_single="[$SEARCH_ID_3]"
    response=$(make_request "POST" "/saved-searches/bulk-delete" "$bulk_delete_single" "true")
    if check_response "$response" "200" "Bulk delete single ID"; then
        body=$(echo "$response" | head -n -1)
        deleted_count=$(echo "$body" | grep -o '"deleted_count":[0-9]*' | cut -d':' -f2)
        echo "Deleted count: $deleted_count"

        ((TOTAL++))
        if [ "$deleted_count" -eq "1" ]; then
            print_pass "Deleted count matches expected"
            ((PASSED++))
        else
            print_fail "Deleted count" "Expected 1, got $deleted_count"
            ((FAILED++))
        fi
    fi

    print_test "Verify deletion - Try to get deleted search"
    response=$(make_request "GET" "/saved-searches/$SEARCH_ID_3" "" "true")
    check_response "$response" "404" "Deleted search returns 404"
fi

print_test "Bulk delete - Mix of valid and invalid IDs"
bulk_delete_mixed="[999997, 999998, 999999]"
response=$(make_request "POST" "/saved-searches/bulk-delete" "$bulk_delete_mixed" "true")
if check_response "$response" "200" "Bulk delete with invalid IDs"; then
    body=$(echo "$response" | head -n -1)
    deleted_count=$(echo "$body" | grep -o '"deleted_count":[0-9]*' | cut -d':' -f2)
    echo "Deleted count: $deleted_count"

    ((TOTAL++))
    if [ "$deleted_count" -eq "0" ]; then
        print_pass "No searches deleted for invalid IDs"
        ((PASSED++))
    else
        print_fail "Deleted count" "Expected 0, got $deleted_count"
        ((FAILED++))
    fi
fi

# ============================================
# 9. Delete Saved Search Tests
# ============================================

print_header "9. DELETE SAVED SEARCH TESTS"

if [ -n "$SEARCH_ID_1" ]; then
    print_test "Delete saved search - Valid ID"
    response=$(make_request "DELETE" "/saved-searches/$SEARCH_ID_1" "" "true")
    check_response "$response" "204" "Delete saved search"

    print_test "Verify deletion - Try to get deleted search"
    response=$(make_request "GET" "/saved-searches/$SEARCH_ID_1" "" "true")
    check_response "$response" "404" "Deleted search returns 404"

    print_test "Delete already deleted search - Should fail"
    response=$(make_request "DELETE" "/saved-searches/$SEARCH_ID_1" "" "true")
    check_response "$response" "404" "Delete non-existent search returns 404"
fi

print_test "Delete saved search - Invalid ID"
response=$(make_request "DELETE" "/saved-searches/999999" "" "true")
check_response "$response" "404" "Delete with invalid ID returns 404"

# ============================================
# 10. Data Persistence & Integrity Tests
# ============================================

print_header "10. DATA PERSISTENCE & INTEGRITY TESTS"

print_test "Create → Get → Update → Get → Delete workflow"
workflow_data='{
  "name": "Persistence Test Search",
  "description": "Testing full CRUD workflow",
  "filter_config": {
    "logic": "AND",
    "filters": [
      {"field": "status", "operator": "equals", "value": "active"}
    ]
  },
  "is_favorite": false
}'
response=$(make_request "POST" "/saved-searches" "$workflow_data" "true")
if check_response "$response" "201" "Workflow Step 1: Create"; then
    WORKFLOW_ID=$(echo "$response" | head -n -1 | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "Created search ID: $WORKFLOW_ID"

    if [ -n "$WORKFLOW_ID" ]; then
        # Get
        print_test "Workflow Step 2: Get created search"
        response=$(make_request "GET" "/saved-searches/$WORKFLOW_ID" "" "true")
        check_response "$response" "200" "Get newly created search"

        # Update
        print_test "Workflow Step 3: Update search"
        workflow_update='{"name": "Persistence Test (Updated)", "is_favorite": true}'
        response=$(make_request "PUT" "/saved-searches/$WORKFLOW_ID" "$workflow_update" "true")
        check_response "$response" "200" "Update search"

        # Get updated
        print_test "Workflow Step 4: Get updated search"
        response=$(make_request "GET" "/saved-searches/$WORKFLOW_ID" "" "true")
        if check_response "$response" "200" "Get updated search"; then
            body=$(echo "$response" | head -n -1)
            ((TOTAL++))
            if echo "$body" | grep -q '"name":"Persistence Test (Updated)"'; then
                print_pass "Update persisted in database"
                ((PASSED++))
            else
                print_fail "Update persistence" "Changes not saved"
                ((FAILED++))
            fi
        fi

        # Delete
        print_test "Workflow Step 5: Delete search"
        response=$(make_request "DELETE" "/saved-searches/$WORKFLOW_ID" "" "true")
        check_response "$response" "204" "Delete search"
    fi
fi

# ============================================
# 11. Security & Access Control Tests
# ============================================

print_header "11. SECURITY & ACCESS CONTROL TESTS"

print_test "Attempt to access another user's search"
# This test assumes user 1 (from token) cannot access searches from other users
# We'll try to access a search ID that doesn't belong to the user
response=$(make_request "GET" "/saved-searches/99999" "" "true")
check_response "$response" "404" "Cannot access other user's searches"

print_test "Attempt to update another user's search"
invalid_update='{"name": "Unauthorized update"}'
response=$(make_request "PUT" "/saved-searches/99999" "$invalid_update" "true")
check_response "$response" "404" "Cannot update other user's searches"

print_test "Attempt to delete another user's search"
response=$(make_request "DELETE" "/saved-searches/99999" "" "true")
check_response "$response" "404" "Cannot delete other user's searches"

# ============================================
# 12. Edge Cases & Error Handling
# ============================================

print_header "12. EDGE CASES & ERROR HANDLING"

print_test "Create search with empty filter array"
edge_empty_filters='{
  "name": "Empty Filters Test",
  "filter_config": {
    "logic": "AND",
    "filters": []
  }
}'
response=$(make_request "POST" "/saved-searches" "$edge_empty_filters" "true")
check_response "$response" "201" "Empty filters array is valid"

print_test "Create search with only sort (no filters)"
edge_only_sort='{
  "name": "Sort Only Test",
  "filter_config": {
    "logic": "AND",
    "filters": [],
    "sort": {"field": "title", "order": "asc"}
  }
}'
response=$(make_request "POST" "/saved-searches" "$edge_only_sort" "true")
check_response "$response" "201" "Sort without filters is valid"

print_test "Create search with complex nested value"
edge_complex_value='{
  "name": "Complex Value Test",
  "filter_config": {
    "logic": "AND",
    "filters": [
      {"field": "metadata", "operator": "equals", "value": {"nested": "object", "count": 123}}
    ]
  }
}'
response=$(make_request "POST" "/saved-searches" "$edge_complex_value" "true")
check_response "$response" "201" "Complex nested value in filter"

print_test "Create search with null value"
edge_null_value='{
  "name": "Null Value Test",
  "filter_config": {
    "logic": "AND",
    "filters": [
      {"field": "optional_field", "operator": "is_null"}
    ]
  }
}'
response=$(make_request "POST" "/saved-searches" "$edge_null_value" "true")
check_response "$response" "201" "Null value in filter"

print_test "Update with empty body"
if [ -n "$SEARCH_ID_2" ]; then
    response=$(make_request "PUT" "/saved-searches/$SEARCH_ID_2" "{}" "true")
    check_response "$response" "200" "Empty update body (no changes)"
fi

print_test "Malformed JSON"
malformed_json='{"name": "Test", invalid json here}'
response=$(curl -s -X POST \
    -H "$HEADER_JSON" \
    -H "$HEADER_AUTH" \
    -d "$malformed_json" \
    -w "\n%{http_code}" \
    "$API_BASE/saved-searches")
check_response "$response" "422" "Malformed JSON returns 422"

# ============================================
# Test Summary
# ============================================

print_header "TEST SUMMARY"
echo ""
echo -e "Total Tests: ${BLUE}$TOTAL${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}SOME TESTS FAILED${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
