# API Examples

Complete examples for all BWARM Dashboard API endpoints with request/response samples.

## Table of Contents
- [Authentication](#authentication)
- [Musical Works](#musical-works)
- [Full-Text Search](#full-text-search)
- [Catalog Operations](#catalog-operations)
- [Admin Operations](#admin-operations)

---

## Authentication

### Login

**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "publisher@test.com",
    "password": "password"
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Incorrect email or password"
}
```

### Refresh Token

**Endpoint**: `POST /api/v1/auth/refresh`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

### Get Current User

**Endpoint**: `GET /api/v1/auth/me`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "id": 2,
  "email": "publisher@test.com",
  "role": "publisher",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Logout

**Endpoint**: `POST /api/v1/auth/logout`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

## Musical Works

### List Works

**Endpoint**: `GET /api/v1/works`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/works?page=1&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "title": "Bohemian Rhapsody",
      "alternate_titles": ["Bo Rhap"],
      "iswc": "T-070.244.478-1",
      "contributors": [
        {
          "name": "Freddie Mercury",
          "role": "composer",
          "ipi_name_number": "00052210040"
        }
      ],
      "duration_seconds": 354,
      "year": 1975,
      "has_disputed_rights": false,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_items": 100,
    "total_pages": 10
  }
}
```

### Search Works

**Endpoint**: `GET /api/v1/works?search=bohemian`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/works?search=bohemian&page=1&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response**: Same format as List Works

### Get Work Details

**Endpoint**: `GET /api/v1/works/{work_id}`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/works/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Bohemian Rhapsody",
  "alternate_titles": ["Bo Rhap"],
  "iswc": "T-070.244.478-1",
  "contributors": [
    {
      "id": 1,
      "name": "Freddie Mercury",
      "role": "composer",
      "ipi_name_number": "00052210040",
      "work_id": 1
    }
  ],
  "resources": [
    {
      "id": 1,
      "resource_type": "musicbrainz",
      "resource_identifier": "mb-123456",
      "work_id": 1
    }
  ],
  "rights_controllers": [
    {
      "id": 1,
      "controller_name": "Queen Productions Ltd",
      "society_affiliation": "PRS",
      "territory": "GB",
      "share_percentage": 100.0,
      "work_id": 1
    }
  ],
  "duration_seconds": 354,
  "year": 1975,
  "has_disputed_rights": false,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### Get Dashboard Statistics

**Endpoint**: `GET /api/v1/works/statistics`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/works/statistics" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "total_works": 10,
  "works_with_iswc": 10,
  "disputed_works": 1,
  "monthly_trend": [
    {
      "month": "2025-01",
      "count": 10
    }
  ]
}
```

---

## Full-Text Search

**New in Week 2**: Elasticsearch-powered full-text search with fuzzy matching, relevance scoring, and autocomplete.

### Search Works (Elasticsearch)

**Endpoint**: `GET /api/v1/search/works`

**Features**:
- Fuzzy matching for typo tolerance
- Multi-field search with boosting (title^3, contributors^2, publisher^1)
- Result highlighting
- Filter by ISWC presence and disputed rights
- Relevance scoring

**Request - Basic Search**:
```bash
curl -X GET "http://localhost:8000/api/v1/search/works?q=beethoven" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Request - Advanced Search with Filters**:
```bash
curl -X GET "http://localhost:8000/api/v1/search/works?q=symphony&has_iswc=true&page=1&limit=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": 1,
      "title": "Symphony No. 9",
      "contributors": "Ludwig van Beethoven",
      "publisher": "Universal Music Publishing",
      "iswc": "T-123.456.789-0",
      "has_disputed_rights": false,
      "created_at": "2025-01-15T10:00:00Z",
      "_score": 12.5,
      "_highlight": {
        "title": ["<em>Symphony</em> No. 9"],
        "contributors": ["Ludwig van <em>Beethoven</em>"]
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "query": "symphony",
  "filters": {
    "has_iswc": true
  },
  "max_score": 12.5
}
```

**Query Parameters**:
- `q` (required): Search query (min 2 characters)
- `has_iswc` (optional): Filter by ISWC presence (true/false)
- `has_disputed_rights` (optional): Filter disputed rights (true/false)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (max 100, default: 20)

### Autocomplete Suggestions

**Endpoint**: `GET /api/v1/search/suggest`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/search/suggest?q=beetho&limit=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "suggestions": [
    {
      "title": "Symphony No. 9",
      "id": 1,
      "contributors": "Ludwig van Beethoven",
      "score": 12.5
    },
    {
      "title": "Piano Sonata No. 14 (Moonlight)",
      "id": 2,
      "contributors": "Ludwig van Beethoven",
      "score": 10.2
    }
  ],
  "query": "beetho"
}
```

**Query Parameters**:
- `q` (required): Partial query string (min 1 character)
- `limit` (optional): Number of suggestions (max 20, default: 5)

### Reindex All Works (Admin Only)

**Endpoint**: `POST /api/v1/search/reindex`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/search/reindex" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (202 Accepted):
```json
{
  "status": "reindexing",
  "message": "Reindexing 10000 works",
  "count": 10000
}
```

**Use Cases**:
- After bulk data imports
- Index corruption recovery
- Elasticsearch cluster migration
- Schema updates

**Note**: Only users with `admin` role can trigger reindexing.

### Search Examples

**Fuzzy Matching (Handles Typos)**:
```bash
# Search for "beethoven" even with typo "bethovn"
curl -X GET "http://localhost:8000/api/v1/search/works?q=bethovn" \
  -H "Authorization: Bearer ..."
```

**Multi-Field Search**:
```bash
# Searches across title, contributors, and publisher
curl -X GET "http://localhost:8000/api/v1/search/works?q=universal+mozart" \
  -H "Authorization: Bearer ..."
```

**Combine Search with Filters**:
```bash
# Find disputed works by Beethoven with ISWC
curl -X GET "http://localhost:8000/api/v1/search/works?q=beethoven&has_iswc=true&has_disputed_rights=true" \
  -H "Authorization: Bearer ..."
```

**Autocomplete for Search Bar**:
```bash
# Get suggestions as user types
curl -X GET "http://localhost:8000/api/v1/search/suggest?q=sym" \
  -H "Authorization: Bearer ..."
```

### Search vs. Works Endpoint

| Feature | `/api/v1/search/works` | `/api/v1/works?search=...` |
|---------|------------------------|---------------------------|
| **Search Engine** | Elasticsearch | PostgreSQL ILIKE |
| **Fuzzy Matching** | ✅ Yes (typo tolerant) | ❌ No |
| **Relevance Scoring** | ✅ Yes | ❌ No |
| **Result Highlighting** | ✅ Yes | ❌ No |
| **Multi-field Boosting** | ✅ Yes (title^3) | ❌ No |
| **Performance** | Fast (indexed) | Slower (full scan) |
| **Use Case** | Primary search | Simple filtering |

**Recommendation**: Use `/api/v1/search/works` for user-facing search features. Use `/api/v1/works?search=...` for simple filtering within works list.

---

## Catalog Operations

### Upload Catalog

**Endpoint**: `POST /api/v1/catalog/upload`

**Request** (multipart/form-data):
```bash
curl -X POST "http://localhost:8000/api/v1/catalog/upload" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@catalog.csv" \
  -F "publisher_name=Universal Music Publishing"
```

**CSV File Example** (`catalog.csv`):
```csv
title,artist,composer,iswc,duration,year
"Bohemian Rhapsody","Queen","Freddie Mercury","T-070.244.478-1",354,1975
"Imagine","John Lennon","John Lennon, Yoko Ono","T-070.244.479-1","3:03",1971
"Let It Be","The Beatles","Paul McCartney","T-070.244.480-1","4:03",1970
```

**Response** (201 Created):
```json
{
  "id": 1,
  "filename": "catalog.csv",
  "publisher_name": "Universal Music Publishing",
  "file_format": "csv",
  "file_size_bytes": 1024,
  "status": "processing",
  "tracks_count": 3,
  "progress_percentage": 0.0,
  "created_at": "2025-01-15T10:30:00Z",
  "user_id": 2,
  "user_email": "publisher@test.com"
}
```

### Get Upload Status

**Endpoint**: `GET /api/v1/catalog/{upload_id}/status`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/1/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response - Processing** (200 OK):
```json
{
  "id": 1,
  "filename": "catalog.csv",
  "publisher_name": "Universal Music Publishing",
  "status": "processing",
  "tracks_count": 500,
  "progress_percentage": 45.5,
  "status_message": "Processing: 227/500 tracks",
  "estimated_time_remaining_seconds": 180,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Response - Completed** (200 OK):
```json
{
  "id": 1,
  "filename": "catalog.csv",
  "publisher_name": "Universal Music Publishing",
  "status": "completed",
  "tracks_count": 500,
  "progress_percentage": 100.0,
  "status_message": "Processing complete",
  "processing_stats": {
    "total_tracks": 500,
    "total_matches": 450,
    "high_confidence_matches": 300,
    "medium_confidence_matches": 100,
    "low_confidence_matches": 50,
    "processing_time_seconds": 45.2
  },
  "created_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:31:00Z"
}
```

### List My Uploads

**Endpoint**: `GET /api/v1/catalog/uploads`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/uploads?page=1&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "filename": "catalog.csv",
      "publisher_name": "Universal Music Publishing",
      "status": "completed",
      "tracks_count": 500,
      "progress_percentage": 100.0,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_items": 5,
    "total_pages": 1
  }
}
```

### Get Match Results

**Endpoint**: `GET /api/v1/catalog/{upload_id}/results`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/1/results?page=1&limit=10&confidence=high" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "uploaded_track": {
        "title": "Bohemian Rhapsody",
        "artist": "Queen",
        "composer": "Freddie Mercury",
        "iswc": "T-070.244.478-1",
        "duration_seconds": 354,
        "year": 1975
      },
      "matches": [
        {
          "match_score": 0.98,
          "confidence_level": "high",
          "rank": 1,
          "matched_work": {
            "id": 1,
            "title": "Bohemian Rhapsody",
            "iswc": "T-070.244.478-1",
            "contributors": [
              {
                "name": "Freddie Mercury",
                "role": "composer"
              }
            ],
            "duration_seconds": 354,
            "year": 1975
          }
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_items": 450,
    "total_pages": 45
  }
}
```

### Export Results

**Endpoint**: `GET /api/v1/catalog/{upload_id}/export`

**Request - CSV**:
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/1/export?format=csv" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -o results.csv
```

**Request - Excel**:
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/1/export?format=excel&confidence=high" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -o results.xlsx
```

**Response**: Binary file download (CSV or Excel)

**CSV Output Example**:
```csv
Uploaded Title,Uploaded Artist,Match Score,Confidence,Matched Title,Matched ISWC,Matched Contributors
"Bohemian Rhapsody","Queen",0.98,high,"Bohemian Rhapsody","T-070.244.478-1","Freddie Mercury (composer)"
```

---

## Admin Operations

**Note**: All admin endpoints require `admin` role.

### List All Users

**Endpoint**: `GET /api/v1/admin/users`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users?page=1&limit=50" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "email": "admin@test.com",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "email": "publisher@test.com",
      "role": "publisher",
      "is_active": true,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_items": 3,
    "total_pages": 1
  }
}
```

### List All Uploads

**Endpoint**: `GET /api/v1/admin/uploads`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/uploads?page=1&limit=50&user_id=2" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "filename": "catalog.csv",
      "publisher_name": "Universal Music Publishing",
      "status": "completed",
      "tracks_count": 500,
      "user_id": 2,
      "user_email": "publisher@test.com",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_items": 10,
    "total_pages": 1
  }
}
```

### Get System Statistics

**Endpoint**: `GET /api/v1/admin/statistics`

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/statistics" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "total_users": 3,
  "active_users": 3,
  "total_uploads": 10,
  "completed_uploads": 8,
  "processing_uploads": 1,
  "failed_uploads": 1,
  "total_works": 10,
  "total_matches": 4500
}
```

### Delete Upload

**Endpoint**: `DELETE /api/v1/catalog/{upload_id}`

**Request**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/catalog/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "message": "Upload deleted successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid file format. Supported formats: csv, xlsx, xls, json, xml"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Work not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Rate limits are enforced per user/IP:
- **Authentication endpoints**: 5 requests/minute
- **Upload endpoints**: 10 requests/hour
- **Other endpoints**: 100 requests/minute

**Rate Limit Response** (429 Too Many Requests):
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Pagination

All list endpoints support pagination with query parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)

Response includes `pagination` object:
```json
{
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_items": 150,
    "total_pages": 3
  }
}
```

---

## Filtering & Sorting

### Works Endpoint Filters
- `search`: Full-text search across title and contributors
- `has_iswc`: Filter by ISWC presence (true/false)
- `has_disputed_rights`: Filter disputed works (true/false)
- `year_min`, `year_max`: Filter by year range

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/works?search=queen&has_iswc=true&year_min=1970&year_max=1980" \
  -H "Authorization: Bearer ..."
```

### Match Results Filters
- `confidence`: Filter by confidence level (high/medium/low)
- `min_score`: Minimum match score (0.0-1.0)

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/1/results?confidence=high&min_score=0.8" \
  -H "Authorization: Bearer ..."
```

---

## Testing with Postman

1. Import the OpenAPI spec: `http://localhost:8000/api/openapi.json`
2. Create environment with `BASE_URL=http://localhost:8000/api/v1`
3. Add `access_token` variable
4. Set Authorization header: `Bearer {{access_token}}`

---

## Testing with cURL Script

```bash
#!/bin/bash

# Base URL
API_URL="http://localhost:8000/api/v1"

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "publisher@test.com", "password": "password"}')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

echo "Access Token: $ACCESS_TOKEN"

# List works
curl -X GET "$API_URL/works?page=1&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Upload catalog
curl -X POST "$API_URL/catalog/upload" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@catalog.csv" \
  -F "publisher_name=Test Publisher"
```
