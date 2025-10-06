# Data Model: BWARM Dashboard

**Feature**: 001-bwarm-dashboard-high
**Date**: 2025-10-04
**Status**: Complete

## Overview
This document defines the data entities, relationships, validation rules, and state transitions for the BWARM Dashboard application.

## Entity Definitions

### 1. Musical Work

**Purpose**: Represents a copyrighted musical composition (the underlying work, not the recording).

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `musical_work_record_id` | String(255) | Unique, required | Business identifier from BWARM source |
| `iswc` | String(15) | Optional, indexed | International Standard Musical Work Code |
| `title` | Text | Required, indexed (GIN full-text) | Work title |
| `title_language_script_code` | String(10) | Optional | ISO language/script code |
| `opus_number` | String(100) | Optional | Classical music opus number |
| `catalogue_number` | Array[String] | Optional, indexed (GIN) | Catalog identifiers |
| `duration` | Interval | Optional | Standard duration of work |
| `has_disputed_right_shares` | Boolean | Required, default=false, indexed | Rights dispute flag |
| `public_domain_territory_codes` | Array[String(2)] | Optional | ISO country codes where work is public domain |
| `is_arrangement_traditional_work` | Boolean | Required, default=false | Traditional/arrangement flag |
| `created_at` | Timestamp with TZ | Auto-generated, indexed | Record creation timestamp |
| `updated_at` | Timestamp with TZ | Auto-updated | Last modification timestamp |

**Validation Rules**:
- `title` must not be empty string
- `iswc` format: `T-###.###.###-#` (if provided)
- `title_language_script_code` must match ISO 15924 (if provided)
- `public_domain_territory_codes` must be valid ISO 3166-1 alpha-2 codes

**Indexes**:
- Primary key: `id`
- Unique: `musical_work_record_id`
- GIN: `to_tsvector('english', title || ' ' || coalesce(catalogue_number::text, ''))`
- Hash: `iswc` (where not null)
- Composite: `(created_at DESC, has_disputed_right_shares)`

**Relationships**:
- One-to-Many: `WorkResourceLink` (a work can have multiple recordings)

---

### 2. Resource

**Purpose**: Represents a sound recording or music video (the specific recorded version).

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `resource_record_id` | String(255) | Unique, required | Business identifier from BWARM source |
| `resource_type` | Enum | Required, values: `SoundRecording`, `MusicVideo` | Type of resource |
| `isrc` | String(12) | Optional, indexed | International Standard Recording Code |
| `title` | Text | Required | Recording title |
| `display_artist_name` | Text | Required | Primary artist name for display |
| `duration` | Interval | Optional | Recording duration |
| `created_at` | Timestamp with TZ | Auto-generated | Record creation timestamp |

**Validation Rules**:
- `title` must not be empty
- `display_artist_name` must not be empty
- `isrc` format: `CC-XXX-YY-NNNNN` (if provided)
- `resource_type` must be one of enumerated values

**Indexes**:
- Primary key: `id`
- Unique: `resource_record_id`
- Hash: `isrc` (where not null)

**Relationships**:
- One-to-Many: `WorkResourceLink` (a resource can link to multiple works)

---

### 3. Work-Resource Link

**Purpose**: Many-to-many relationship between musical works and their recordings/videos.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `musical_work_id` | UUID | Foreign key, required | Reference to Musical Work |
| `resource_id` | UUID | Foreign key, required | Reference to Resource |
| `created_at` | Timestamp with TZ | Auto-generated | Link creation timestamp |

**Validation Rules**:
- `musical_work_id` must reference existing Musical Work
- `resource_id` must reference existing Resource
- Combination (`musical_work_id`, `resource_id`) must be unique

**Indexes**:
- Primary key: `id`
- Unique: `(musical_work_id, resource_id)`
- Foreign keys: `musical_work_id`, `resource_id`

---

### 4. User

**Purpose**: Represents authenticated users (Publishers and Admins).

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `email` | String(255) | Unique, required, indexed | User email (login identifier) |
| `hashed_password` | String(255) | Required | Bcrypt hashed password |
| `full_name` | String(255) | Required | User's display name |
| `role` | Enum | Required, values: `publisher`, `admin` | User role |
| `is_active` | Boolean | Required, default=true | Account active status |
| `created_at` | Timestamp with TZ | Auto-generated | Account creation timestamp |
| `last_login_at` | Timestamp with TZ | Optional, updated on login | Last successful login |

**Validation Rules**:
- `email` must be valid email format
- `hashed_password` length must be 60 chars (bcrypt standard)
- `role` must be `publisher` or `admin`
- `full_name` must not be empty

**Indexes**:
- Primary key: `id`
- Unique: `email`

**Relationships**:
- One-to-Many: `CatalogUpload` (user owns multiple uploads)

---

### 5. Catalog Upload

**Purpose**: Tracks publisher catalog file uploads and processing status.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `user_id` | UUID | Foreign key, required, indexed | Owner of upload |
| `publisher_name` | String(255) | Required | Publisher business name |
| `upload_filename` | String(500) | Required | Original filename |
| `file_format` | Enum | Required, values: `csv`, `excel`, `json`, `xml` | Uploaded file type |
| `file_size` | BigInt | Required | File size in bytes |
| `status` | Enum | Required, default=`uploading`, indexed | Processing status |
| `total_tracks` | Integer | Default=0 | Total tracks in catalog |
| `processed_tracks` | Integer | Default=0 | Tracks processed so far |
| `matched_tracks` | Integer | Default=0 | Tracks with at least one match |
| `upload_date` | Timestamp with TZ | Auto-generated, indexed | Upload start timestamp |
| `processing_started_at` | Timestamp with TZ | Optional | Processing start timestamp |
| `processing_completed_at` | Timestamp with TZ | Optional | Processing completion timestamp |

**Validation Rules**:
- `file_size` must be > 0 and ≤ 524,288,000 (500MB)
- `file_format` must be one of: `csv`, `excel`, `json`, `xml`
- `status` must be one of: `uploading`, `processing`, `completed`, `failed`
- `processed_tracks` ≤ `total_tracks`
- `matched_tracks` ≤ `processed_tracks`

**Indexes**:
- Primary key: `id`
- Foreign key: `user_id`
- Composite: `(user_id, upload_date DESC)` for user's upload history
- Index: `status` for filtering by status

**State Transitions**:
```
uploading → processing → completed
            ↓
          failed
```

**Relationships**:
- Many-to-One: `User` (upload belongs to one user)
- One-to-Many: `CatalogMatch` (upload has multiple match results)

---

### 6. Catalog Match

**Purpose**: Stores match results between uploaded catalog tracks and BWARM works.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `upload_id` | UUID | Foreign key, required, indexed | Reference to catalog upload |
| `uploaded_track_title` | Text | Required | Track title from catalog |
| `uploaded_track_artist` | Text | Optional | Artist name from catalog |
| `uploaded_track_iswc` | String(15) | Optional | ISWC from catalog (if present) |
| `uploaded_track_duration` | Interval | Optional | Duration from catalog |
| `matched_work_id` | UUID | Foreign key, required, indexed | Reference to matched Musical Work |
| `match_score` | Decimal(5,4) | Required, range: 0.0000-1.0000 | Similarity score |
| `confidence_level` | Enum | Required, values: `high`, `medium`, `low` | Confidence classification |
| `matching_algorithm` | String(50) | Required | Algorithm identifier |
| `created_at` | Timestamp with TZ | Auto-generated | Match creation timestamp |

**Validation Rules**:
- `match_score` must be between 0.0000 and 1.0000
- `confidence_level` must be one of: `high`, `medium`, `low`
- Confidence mapping: high (≥0.85), medium (0.70-0.84), low (<0.70)
- `uploaded_track_title` must not be empty
- `matched_work_id` must reference existing Musical Work

**Indexes**:
- Primary key: `id`
- Foreign keys: `upload_id`, `matched_work_id`
- Composite: `(upload_id, match_score DESC)` for sorted results
- Index: `confidence_level` for filtering

**Relationships**:
- Many-to-One: `CatalogUpload` (match belongs to one upload)
- Many-to-One: `MusicalWork` (match references one work)

---

### 7. User Preferences

**Purpose**: Stores user-specific dashboard customization and application preferences.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `user_id` | UUID | Foreign key, required, unique | Reference to User (one-to-one) |
| `dashboard_layout` | JSONB | Optional | Saved dashboard widget configuration and positions |
| `saved_searches` | JSONB | Optional | Array of saved search/filter combinations |
| `theme` | Enum | Required, default=`light` | UI theme preference |
| `items_per_page` | Integer | Required, default=50 | Pagination preference |
| `notification_email_enabled` | Boolean | Required, default=true | Email notification preference |
| `notification_browser_enabled` | Boolean | Required, default=true | Browser notification preference |
| `language` | String(10) | Required, default=`en` | ISO language code |
| `timezone` | String(50) | Required, default=`UTC` | IANA timezone identifier |
| `created_at` | Timestamp with TZ | Auto-generated | Record creation timestamp |
| `updated_at` | Timestamp with TZ | Auto-updated | Last modification timestamp |

**Validation Rules**:
- `user_id` must reference existing User and be unique (one user = one preferences record)
- `theme` must be one of: `light`, `dark`, `auto`
- `items_per_page` must be between 10 and 200
- `language` must be valid ISO 639-1 code
- `timezone` must be valid IANA timezone string
- `dashboard_layout` JSON schema: `{ widgets: Array<{ id: string, position: { x, y, w, h } }> }`
- `saved_searches` JSON schema: `Array<{ name: string, filters: object, created_at: string }>`

**Indexes**:
- Primary key: `id`
- Unique: `user_id`
- Foreign key: `user_id`

**Relationships**:
- One-to-One: `User` (each user has one preferences record)

---

### 8. Notification

**Purpose**: Tracks user notifications for important events and status updates.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `user_id` | UUID | Foreign key, required, indexed | Recipient user |
| `type` | Enum | Required, indexed | Notification type classification |
| `title` | String(255) | Required | Notification headline |
| `message` | Text | Required | Notification body content |
| `related_entity_type` | String(50) | Optional | Type of related entity (e.g., "catalog_upload") |
| `related_entity_id` | UUID | Optional, indexed | ID of related entity |
| `severity` | Enum | Required, default=`info` | Severity level for visual styling |
| `is_read` | Boolean | Required, default=false, indexed | Read status |
| `is_dismissed` | Boolean | Required, default=false | Dismiss status |
| `action_url` | String(500) | Optional | Link for "View" action |
| `created_at` | Timestamp with TZ | Auto-generated, indexed | Notification creation timestamp |
| `read_at` | Timestamp with TZ | Optional | Timestamp when marked as read |
| `expires_at` | Timestamp with TZ | Optional | Auto-dismiss after expiration |

**Validation Rules**:
- `user_id` must reference existing User
- `type` must be one of: `upload_complete`, `upload_failed`, `match_found`, `system_alert`, `info`
- `severity` must be one of: `info`, `success`, `warning`, `error`
- `title` must not be empty
- `message` must not be empty
- `related_entity_id` should be provided when `related_entity_type` is set
- `action_url` must be valid relative or absolute URL if provided

**Indexes**:
- Primary key: `id`
- Foreign key: `user_id`
- Composite: `(user_id, is_read, created_at DESC)` for user's unread notifications
- Composite: `(user_id, created_at DESC)` for user's notification feed
- Index: `related_entity_id` for entity-related queries
- Index: `expires_at` for cleanup job

**Relationships**:
- Many-to-One: `User` (notification belongs to one user)
- Optional reference to: `CatalogUpload` (via `related_entity_id` when `related_entity_type='catalog_upload'`)

---

### 9. Activity Log

**Purpose**: Audit trail for user actions and system events for security and compliance.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier |
| `user_id` | UUID | Foreign key, optional, indexed | User who performed action (null for system events) |
| `action` | String(100) | Required, indexed | Action type identifier |
| `entity_type` | String(50) | Optional | Type of entity affected |
| `entity_id` | UUID | Optional, indexed | ID of entity affected |
| `description` | Text | Required | Human-readable action description |
| `metadata` | JSONB | Optional | Additional structured data about the action |
| `ip_address` | String(45) | Optional | Client IP address (IPv4 or IPv6) |
| `user_agent` | String(500) | Optional | Client user agent string |
| `status` | Enum | Required | Action result status |
| `error_message` | Text | Optional | Error details if status is failed |
| `created_at` | Timestamp with TZ | Auto-generated, indexed | Action timestamp |

**Validation Rules**:
- `action` must follow format: `{entity}.{verb}` (e.g., "catalog.upload", "user.login")
- `status` must be one of: `success`, `failed`, `pending`
- `description` must not be empty
- `ip_address` must be valid IPv4 or IPv6 format if provided
- `metadata` JSON schema varies by action type but should be documented per action

**Common Action Types**:
- `user.login`, `user.logout`, `user.register`, `user.update_profile`
- `catalog.upload`, `catalog.delete`, `catalog.export_results`
- `search.execute`, `filter.apply`
- `preferences.update`, `notification.mark_read`

**Indexes**:
- Primary key: `id`
- Foreign key: `user_id`
- Composite: `(user_id, created_at DESC)` for user's activity history
- Composite: `(action, created_at DESC)` for action-specific queries
- Composite: `(entity_type, entity_id, created_at DESC)` for entity audit trail
- Index: `created_at` for time-based queries and retention cleanup

**Relationships**:
- Many-to-One: `User` (activity performed by one user, nullable for system events)

---

## Entity Relationship Diagram

```
┌──────────────┐         ┌─────────────────┐         ┌──────────────┐
│ MusicalWork  │◄────────│WorkResourceLink │────────►│   Resource   │
└──────────────┘         └─────────────────┘         └──────────────┘
      ▲
      │ matched_work_id
      │
┌─────┴────────┐         ┌─────────────────┐         ┌──────────────┐
│CatalogMatch  │◄────────│  CatalogUpload  │◄────────│     User     │
└──────────────┘         └─────────────────┘         └──────┬───────┘
 (Many)          upload_id (One)      user_id (One)         │
                                                             │ user_id (1:1)
                                                             ▼
                                               ┌─────────────────────┐
                                               │  UserPreferences   │
                                               └─────────────────────┘
                                                             ▲
                                                             │ user_id
                ┌────────────────┐                          │
                │  Notification  │◄─────────────────────────┘
                └────────────────┘
                         ▲
                         │ user_id (optional)
                         │
                ┌────────┴───────┐
                │  ActivityLog   │
                └────────────────┘
```

## Data Volume Estimates

| Entity | Estimated Count | Growth Rate |
|--------|----------------|-------------|
| Musical Work | 10-50 million | +1% monthly (new works) |
| Resource | 20-100 million | +2% monthly (new recordings) |
| Work-Resource Link | 30-150 million | +2% monthly |
| User | 100-10,000 | +10% monthly (user acquisition) |
| Catalog Upload | 1,000-100,000 | +20% monthly (active usage) |
| Catalog Match | 100K-10M | +20% monthly (proportional to uploads) |
| User Preferences | 100-10,000 | +10% monthly (1:1 with users) |
| Notification | 10K-1M | +25% monthly (multiple per user) |
| Activity Log | 100K-10M | +30% monthly (multiple per user action) |

## Storage Considerations

- **Musical Work**: Avg 500 bytes/record → 25GB for 50M records
- **Resource**: Avg 300 bytes/record → 30GB for 100M records
- **Work-Resource Link**: Avg 50 bytes/record → 7.5GB for 150M records
- **Catalog Match**: Avg 200 bytes/record → 2GB for 10M records
- **User Preferences**: Avg 2KB/record (JSONB fields) → 20MB for 10K records
- **Notification**: Avg 400 bytes/record → 400MB for 1M records
- **Activity Log**: Avg 500 bytes/record → 5GB for 10M records
- **Total estimated**: ~70GB + indexes (~2x) + overhead = **~155GB**

Note: 2TB mentioned in requirements likely refers to total PostgreSQL database size including all BWARM data, not just entities defined here.

## Data Retention Policies

| Entity | Retention Policy |
|--------|------------------|
| Musical Work | Permanent (core reference data) |
| Resource | Permanent (core reference data) |
| Work-Resource Link | Permanent (core reference data) |
| User | Indefinite (deleted on explicit request) |
| Catalog Upload | Indefinite until user/admin deletes |
| Catalog Match | Indefinite until user/admin deletes |
| User Preferences | Indefinite (deleted with user account) |
| Notification | 90 days (auto-cleanup of read notifications) |
| Activity Log | 1 year (compliance requirement, then archived or purged) |

---

*Data model completed: 2025-10-04*
*Updated: 2025-10-05 (added UserPreferences, Notification, ActivityLog)*
*Ready for API contract generation*
