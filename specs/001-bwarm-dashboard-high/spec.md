# Feature Specification: BWARM Dashboard

**Feature Branch**: `001-bwarm-dashboard-high`
**Created**: 2025-10-04
**Status**: Draft
**Input**: User description: "BWARM Dashboard - High-performance web application for managing 2TB BWARM database with catalog matching capabilities for music publishers"

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

---

## Clarifications

### Session 2025-10-04
- Q: When one uploaded track matches multiple BWARM works, how should the system present these results to the user? → A: Show all matches regardless of score with visual ranking
- Q: What user roles exist in the system and what are their distinct permissions? → A: Two roles: Publisher (upload/manage own catalogs) + Admin (view all uploads, manage users, system config)
- Q: How long should the system retain uploaded catalogs and their match results? → A: Indefinitely until user manually deletes
- Q: How should the system handle file upload security scanning? → A: Basic validation only (file type, size, structure) - no virus scanning
- Q: When duplicate songs exist in an uploaded catalog, how should the system handle them? → A: Merge duplicates before matching (combine into single entry with metadata merge strategy)

## User Scenarios & Testing

### User Roles
- **Publisher**: Music publishers who can browse the BWARM database, upload their catalogs for matching, and manage their own uploads and results
- **Admin**: System administrators who can view all user uploads, manage user accounts, configure system settings, and access all publisher data for support purposes

### Primary User Story
Music publishers need to identify uncollected royalties by matching their catalog against a massive BWARM (Bulk communication of Work And Recording Metadata) database containing 2TB of musical works and recordings. Publishers upload their catalogs in various formats, and the system identifies which of their songs appear in the BWARM database, helping them discover potential revenue sources they may have missed.

### Acceptance Scenarios

1. **Given** a publisher has a catalog of 5,000 songs in CSV format, **When** they upload the file to the dashboard, **Then** the system processes the file, matches songs against the BWARM database, and displays results showing which songs were found with confidence levels (high/medium/low).

2. **Given** a user is viewing the BWARM database dashboard, **When** they search for "yesterday" in the title field, **Then** the system returns all matching musical works within 500ms and displays them in a paginated, filterable table.

3. **Given** a publisher has uploaded their catalog and matching is complete, **When** they view the results, **Then** they can see detailed match information including song title, artist, match score, confidence level, and can export the results to CSV or Excel.

4. **Given** multiple users are simultaneously browsing the dashboard, **When** 100+ concurrent users search and filter data, **Then** the system maintains response times under 3 seconds for page loads and under 500ms for queries.

5. **Given** a large publisher uploads a 500MB catalog file with 50,000 tracks, **When** the system processes the upload, **Then** it provides real-time progress updates and completes matching within 10 minutes at minimum 1,000 tracks per minute.

### Edge Cases
- What happens when a publisher uploads a file in an unsupported format?
- What if a song in the publisher's catalog has multiple potential matches in the BWARM database?
- How does the system behave when matching algorithms produce low confidence scores for all potential matches?
- What happens if file upload is interrupted mid-process?
- How does the system handle very long song titles or artist names that exceed expected lengths?

## Requirements

### Functional Requirements

#### Dashboard & Browse Functionality
- **FR-001**: System MUST display the BWARM database contents in a searchable, filterable, paginated interface
- **FR-002**: Users MUST be able to search musical works by title, ISWC code, catalog number, and other identifying attributes
- **FR-003**: Users MUST be able to filter works by disputed rights status, public domain territories, and date ranges
- **FR-004**: System MUST display detailed information for each musical work including title, ISWC, opus number, catalog number, duration, and associated recordings
- **FR-005**: System MUST provide dashboard statistics showing total works, works with ISWC codes, disputed works, and monthly trends
- **FR-006**: System MUST support viewing and browsing sound recordings and music videos linked to musical works

#### Catalog Upload & Processing
- **FR-007**: System MUST accept catalog uploads in CSV, Excel, JSON, and XML formats
- **FR-008**: System MUST validate uploaded files for format correctness and provide clear error messages for invalid files
- **FR-009**: System MUST support file uploads up to 500MB in size
- **FR-010**: System MUST track upload status for each submitted catalog (uploading, processing, completed, failed)
- **FR-011**: System MUST provide real-time progress updates during catalog processing
- **FR-012**: System MUST allow publishers to view all their previous uploads and their current status
- **FR-013**: System MUST allow publishers to delete their uploaded catalogs and associated results
- **FR-014**: System MUST detect duplicate songs in uploaded catalogs and merge them into single entries before matching, combining metadata from all duplicate instances

#### Catalog Matching
- **FR-015**: System MUST match uploaded catalog tracks against BWARM database using song title, artist name, ISWC code, duration, and release year
- **FR-016**: System MUST assign a match score (0.0 to 1.0) to each potential match
- **FR-017**: System MUST classify matches into confidence levels: high (score ≥0.85), medium (0.70-0.84), or low (<0.70)
- **FR-018**: System MUST prioritize exact ISWC code matches as 100% confidence
- **FR-019**: System MUST handle cases where one uploaded track matches multiple BWARM works by displaying all matches regardless of score with visual ranking by match score
- **FR-020**: System MUST track which matching algorithm was used for each match result

#### Results & Export
- **FR-021**: Users MUST be able to view detailed match results including uploaded track information, matched BWARM work details, match score, and confidence level
- **FR-022**: System MUST allow filtering match results by confidence level
- **FR-023**: System MUST provide export functionality for match results in CSV and Excel formats
- **FR-024**: Exported results MUST include all relevant match information: uploaded track details, matched work details, match scores, and confidence levels

#### Performance Requirements
- **FR-025**: System MUST load dashboard pages within 3 seconds for 95th percentile of requests
- **FR-026**: System MUST return search and filter results within 500ms for 90th percentile of queries
- **FR-027**: System MUST support 100+ concurrent users without performance degradation
- **FR-028**: System MUST process catalog matching at minimum 1,000 tracks per minute
- **FR-029**: System MUST handle small catalogs (1-1,000 tracks) in 10-30 seconds
- **FR-030**: System MUST handle medium catalogs (1,000-10,000 tracks) in 30-120 seconds
- **FR-031**: System MUST handle large catalogs (10,000+ tracks) in 2-10 minutes

#### Authentication & Security
- **FR-032**: System MUST require user authentication to access the dashboard
- **FR-033**: System MUST support session management with automatic timeout
- **FR-034**: System MUST validate all uploaded files for type and size before processing
- **FR-035**: System MUST validate uploaded files for correct file type, size limits, and structural integrity (no virus scanning required)
- **FR-036**: System MUST log all file upload operations for audit purposes
- **FR-037**: System MUST ensure publishers can only view and manage their own uploaded catalogs
- **FR-038**: System MUST support role-based access with two roles: Publisher (can browse BWARM data, upload and manage own catalogs) and Admin (can view all user uploads, manage user accounts, and configure system settings)

#### Reliability & Availability
- **FR-039**: System MUST maintain 99.9% uptime
- **FR-040**: System MUST maintain API error rate below 0.1%
- **FR-041**: System MUST recover gracefully from processing failures and allow retry
- **FR-042**: System MUST preserve uploaded catalogs and match results indefinitely until explicitly deleted by the user or admin

### Key Entities

- **Musical Work**: Represents a copyrighted musical composition with attributes including unique identifier, ISWC code (optional), title, language, opus number, catalog numbers, duration, disputed rights status, public domain territories, and arrangement status

- **Resource**: Represents a sound recording or music video with attributes including unique identifier, ISRC code (optional), resource type (sound recording or music video), title, display artist name, and duration

- **Work-Resource Link**: Represents the relationship between musical works and their recordings/videos, allowing multiple recordings to be associated with a single composition

- **Catalog Upload**: Represents a publisher's uploaded catalog submission with attributes including publisher name, filename, file format, file size, processing status, track counts (total, processed, matched), and timestamps (upload, processing start, processing completion)

- **Catalog Match**: Represents a match between an uploaded catalog track and a BWARM musical work, including uploaded track information (title, artist, ISWC), matched work reference, match score, confidence level, and matching algorithm used

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
