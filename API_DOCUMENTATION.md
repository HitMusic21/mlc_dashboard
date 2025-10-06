# BWARM Dashboard API Documentation

## Overview

The BWARM Dashboard backend provides a RESTful API built with FastAPI, supporting authentication, works management, catalog matching, notifications, and user preferences.

**Base URL**: `http://localhost:8000/api/v1`
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)
**Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## Authentication

### JWT Token Authentication

All protected endpoints require a valid JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

#### POST /auth/login
Login with email and password to receive access and refresh tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "admin",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### POST /auth/refresh
Refresh an expired access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST /auth/logout
Invalidate current session tokens.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

## Works

### GET /works
Retrieve paginated list of musical works.

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 50, max: 100)
- `search` (string, optional): Search by title, writer, or work ID
- `status` (string, optional): Filter by status (pending, matched, unmatched)
- `sort_by` (string, optional): Sort field (created_at, title, status)
- `sort_order` (string, optional): Sort order (asc, desc)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "work_id": "W123456",
      "title": "Symphony No. 5",
      "writer": "Beethoven, Ludwig van",
      "status": "matched",
      "confidence_score": 98.5,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 50,
  "has_more": true
}
```

### GET /works/{work_id}
Retrieve a specific work by ID.

**Path Parameters:**
- `work_id` (int): Work ID

**Response (200 OK):**
```json
{
  "id": 1,
  "work_id": "W123456",
  "title": "Symphony No. 5",
  "writer": "Beethoven, Ludwig van",
  "iswc": "T-123.456.789-0",
  "status": "matched",
  "confidence_score": 98.5,
  "matched_catalog_id": 456,
  "metadata": {
    "duration": 420,
    "genre": "Classical",
    "year": 1808
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### POST /works
Create a new work entry (Admin only).

**Request Body:**
```json
{
  "work_id": "W789012",
  "title": "Moonlight Sonata",
  "writer": "Beethoven, Ludwig van",
  "iswc": "T-987.654.321-0",
  "metadata": {
    "duration": 360,
    "genre": "Classical"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "work_id": "W789012",
  "title": "Moonlight Sonata",
  ...
}
```

### PUT /works/{work_id}
Update an existing work (Admin only).

**Path Parameters:**
- `work_id` (int): Work ID

**Request Body:** (partial update supported)
```json
{
  "status": "matched",
  "confidence_score": 95.0,
  "matched_catalog_id": 789
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "work_id": "W123456",
  "status": "matched",
  ...
}
```

### DELETE /works/{work_id}
Delete a work (Admin only).

**Path Parameters:**
- `work_id` (int): Work ID

**Response (204 No Content)**

## Catalog

### GET /catalog/matches
Search catalog for potential matches to a work.

**Query Parameters:**
- `query` (string, required): Search query (title, composer, ISWC)
- `limit` (int, optional): Max results (default: 20, max: 100)
- `min_confidence` (float, optional): Minimum confidence score (0-100, default: 50)

**Response (200 OK):**
```json
{
  "matches": [
    {
      "catalog_id": 456,
      "title": "Symphony No. 5 in C minor",
      "composer": "Beethoven, Ludwig van",
      "iswc": "T-123.456.789-0",
      "confidence_score": 98.5,
      "match_reasons": [
        "Exact ISWC match",
        "Title similarity: 95%",
        "Composer match"
      ],
      "metadata": {
        "publisher": "Universal Music",
        "year": 1808
      }
    }
  ],
  "total_matches": 1,
  "query_time_ms": 45
}
```

### POST /catalog/accept-match
Accept a catalog match for a work.

**Request Body:**
```json
{
  "work_id": 1,
  "catalog_id": 456,
  "confidence_score": 98.5
}
```

**Response (200 OK):**
```json
{
  "work_id": 1,
  "catalog_id": 456,
  "status": "matched",
  "matched_at": "2024-01-15T12:00:00Z"
}
```

### POST /catalog/reject-match
Reject a catalog match.

**Request Body:**
```json
{
  "work_id": 1,
  "catalog_id": 456,
  "reason": "Incorrect composer attribution"
}
```

**Response (200 OK):**
```json
{
  "message": "Match rejected successfully"
}
```

### POST /catalog/upload
Upload a catalog file for processing (Admin only).

**Request:** multipart/form-data
- `file`: CSV or Excel file
- `publisher_name` (optional): Publisher name

**Response (202 Accepted):**
```json
{
  "upload_id": 789,
  "filename": "catalog_2024_01.csv",
  "status": "processing",
  "estimated_time_seconds": 120
}
```

### GET /catalog/uploads
Get catalog upload history.

**Query Parameters:**
- `page` (int, optional): Page number
- `limit` (int, optional): Items per page
- `status` (string, optional): Filter by status (pending, processing, completed, failed)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 789,
      "filename": "catalog_2024_01.csv",
      "publisher_name": "Universal Music",
      "status": "completed",
      "total_records": 5000,
      "processed_records": 5000,
      "created_at": "2024-01-15T09:00:00Z",
      "completed_at": "2024-01-15T09:05:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

## Notifications

### GET /notifications
Get user notifications.

**Query Parameters:**
- `page` (int, optional): Page number
- `limit` (int, optional): Items per page (max: 100)
- `is_read` (bool, optional): Filter by read status
- `type` (string, optional): Filter by type (info, success, warning, error)

**Response (200 OK):**
```json
{
  "notifications": [
    {
      "id": "notif_123",
      "user_id": 1,
      "type": "success",
      "severity": "medium",
      "title": "Match Found",
      "message": "New catalog match found for 'Symphony No. 5'",
      "is_read": false,
      "related_entity_type": "work",
      "related_entity_id": "1",
      "action_url": "/works/1",
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 20,
  "has_more": false
}
```

### GET /notifications/unread-count
Get count of unread notifications.

**Response (200 OK):**
```json
{
  "unread_count": 5
}
```

### PUT /notifications/{notification_id}/read
Mark a notification as read.

**Path Parameters:**
- `notification_id` (string): Notification ID

**Response (200 OK):**
```json
{
  "id": "notif_123",
  "is_read": true,
  "read_at": "2024-01-15T15:00:00Z"
}
```

### PUT /notifications/mark-all-read
Mark all notifications as read.

**Response (200 OK):**
```json
{
  "marked_count": 5
}
```

### DELETE /notifications/{notification_id}
Delete a notification.

**Path Parameters:**
- `notification_id` (string): Notification ID

**Response (204 No Content)**

### DELETE /notifications/clear-read
Delete all read notifications.

**Response (200 OK):**
```json
{
  "deleted_count": 10
}
```

## User Preferences

### GET /preferences
Get current user's preferences.

**Response (200 OK):**
```json
{
  "id": "pref_123",
  "user_id": 1,
  "theme": "dark",
  "items_per_page": 50,
  "dashboard_layout": {
    "columns": 12,
    "widgets": [
      {
        "id": "stat-1",
        "type": "stat",
        "position": { "x": 0, "y": 0, "w": 12, "h": 1 }
      },
      {
        "id": "chart-1",
        "type": "chart",
        "position": { "x": 0, "y": 1, "w": 8, "h": 2 }
      }
    ]
  },
  "saved_searches": [
    {
      "name": "Pending Works",
      "filters": { "status": "pending" }
    }
  ],
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T16:00:00Z"
}
```

### PUT /preferences
Update user preferences.

**Request Body:** (partial update supported)
```json
{
  "theme": "light",
  "items_per_page": 100
}
```

**Response (200 OK):**
```json
{
  "id": "pref_123",
  "theme": "light",
  "items_per_page": 100,
  ...
}
```

### PUT /preferences/dashboard-layout
Update dashboard layout.

**Request Body:**
```json
{
  "layout": {
    "columns": 12,
    "widgets": [
      {
        "id": "stat-1",
        "type": "stat",
        "position": { "x": 0, "y": 0, "w": 6, "h": 1 }
      }
    ]
  }
}
```

**Response (200 OK):**
```json
{
  "dashboard_layout": { ... }
}
```

### POST /preferences/saved-searches
Save a new search filter.

**Request Body:**
```json
{
  "name": "High Confidence Matches",
  "filters": {
    "status": "matched",
    "confidence_score": { "min": 90 }
  }
}
```

**Response (201 Created):**
```json
{
  "saved_searches": [
    {
      "name": "High Confidence Matches",
      "filters": { ... }
    }
  ]
}
```

## Statistics

### GET /statistics/dashboard
Get dashboard statistics.

**Query Parameters:**
- `period` (string, optional): Time period (day, week, month, year, all)

**Response (200 OK):**
```json
{
  "total_works": 1500,
  "matched_works": 1200,
  "pending_works": 250,
  "unmatched_works": 50,
  "match_rate": 80.0,
  "avg_confidence_score": 92.5,
  "recent_uploads": 15,
  "activity_trend": [
    { "date": "2024-01-15", "matched": 45, "pending": 12 }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "errors": {
    "limit": ["Must be between 1 and 100"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
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
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "request_id": "req_abc123"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated**: 100 requests per hour
- **Admin users**: 5000 requests per hour

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1705329600
```

## Pagination

List endpoints support cursor-based and offset-based pagination:

**Offset-based (default):**
- `page`: Page number (1-indexed)
- `limit`: Items per page

**Response includes:**
```json
{
  "data": [...],
  "total": 150,
  "page": 1,
  "limit": 50,
  "has_more": true
}
```

## Filtering and Sorting

Many list endpoints support filtering and sorting:

**Filters:**
- Use query parameters with exact matches or operators
- Example: `?status=pending&confidence_score[gte]=80`

**Sorting:**
- `sort_by`: Field name
- `sort_order`: `asc` or `desc`
- Example: `?sort_by=created_at&sort_order=desc`

## Webhooks

Subscribe to events via webhooks (Admin only).

### POST /webhooks
Create a webhook subscription.

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["work.matched", "catalog.uploaded"],
  "secret": "webhook_secret_123"
}
```

**Webhook Payload Example:**
```json
{
  "event": "work.matched",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "work_id": 1,
    "catalog_id": 456,
    "confidence_score": 98.5
  }
}
```

## SDK Examples

### JavaScript/TypeScript
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Login
const { data } = await api.post('/auth/login', {
  email: 'user@example.com',
  password: 'password123'
});

// Set token for future requests
api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;

// Get works
const works = await api.get('/works', {
  params: { page: 1, limit: 50, status: 'pending' }
});
```

### Python
```python
import requests

BASE_URL = 'http://localhost:8000/api/v1'

# Login
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'user@example.com',
    'password': 'password123'
})
token = response.json()['access_token']

# Get works
headers = {'Authorization': f'Bearer {token}'}
works = requests.get(
    f'{BASE_URL}/works',
    headers=headers,
    params={'page': 1, 'limit': 50, 'status': 'pending'}
)
```

---

**API Version**: v1
**Last Updated**: 2024-01-15
**Contact**: support@bwarm.com
