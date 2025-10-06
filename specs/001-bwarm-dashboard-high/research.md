# Technical Research: BWARM Dashboard

**Feature**: 001-bwarm-dashboard-high
**Date**: 2025-10-04
**Status**: Complete

## Overview
This document consolidates technical research and design decisions for the BWARM Dashboard implementation, focusing on performance optimization for 2TB database queries, catalog matching algorithms, and scalable architecture choices.

## 1. Database Strategy for 2TB Performance

### Decision: PostgreSQL 15+ with Strategic Indexing + Elasticsearch + Redis

**Rationale**:
- PostgreSQL provides ACID compliance for financial data (royalty tracking)
- GIN indexes enable full-text search on musical work titles and catalog numbers
- Hash indexes optimize exact ISWC/ISRC lookups (O(1) average case)
- Composite indexes support multi-column filtering (disputed rights + date ranges)
- Materialized views cache expensive aggregations for dashboard statistics
- Elasticsearch offloads complex search queries from PostgreSQL
- Redis caches frequent queries and user sessions

**Alternatives Considered**:
- **MongoDB**: Rejected due to weaker ACID guarantees for financial data and less mature full-text search
- **Single PostgreSQL without caching**: Rejected due to inability to meet <500ms query requirements at scale
- **DynamoDB**: Rejected due to complex query patterns requiring multiple GSIs and higher cost

**Implementation Approach**:
- GIN index on `to_tsvector` for title/catalog search
- Hash indexes on ISWC/ISRC for exact match lookups
- Composite B-tree indexes for filtered browsing (status + date)
- Materialized view refresh strategy: nightly for statistics, on-demand for critical data
- Elasticsearch sync via change data capture or application-level updates
- Redis TTL strategy: 5 minutes for query results, 30 minutes for user sessions

## 2. String Similarity Algorithms for Catalog Matching

### Decision: Multi-Algorithm Weighted Scoring (Jaro-Winkler + Levenshtein + Cosine Similarity)

**Rationale**:
- **Jaro-Winkler** (40% weight): Optimized for short strings like song titles, handles transpositions well
- **Levenshtein** (30% weight): Robust for artist names with spelling variations
- **Cosine Similarity via TF-IDF** (20% weight): Captures semantic similarity for longer metadata
- **Duration comparison** (10% weight): Validates matches using objective timing data
- Weighted approach achieves 85-95% accuracy target per requirements

**Alternatives Considered**:
- **Single algorithm (Levenshtein only)**: Rejected - insufficient accuracy for complex music metadata
- **Machine learning model**: Deferred to Phase 4 as enhancement - requires labeled training data and adds complexity
- **Exact matching only**: Rejected - misses legitimate matches due to spelling variations, encoding differences

**Implementation Approach**:
```python
def calculate_match_score(uploaded: Track, bwarm: Work) -> MatchResult:
    # Priority 1: Exact ISWC match = 100% confidence
    if uploaded.iswc and uploaded.iswc == bwarm.iswc:
        return MatchResult(score=1.0, confidence='high')

    # Weighted similarity calculation
    scores = {
        'title': jaro_winkler(normalize(uploaded.title), normalize(bwarm.title)) * 0.40,
        'artist': levenshtein_ratio(normalize(uploaded.artist), normalize(bwarm.artist)) * 0.30,
        'duration': duration_similarity(uploaded.duration, bwarm.duration) * 0.20,
        'year': year_similarity(uploaded.year, bwarm.year) * 0.10
    }

    final_score = sum(scores.values())
    confidence = 'high' if final_score >= 0.85 else 'medium' if final_score >= 0.70 else 'low'
    return MatchResult(score=final_score, confidence=confidence)
```

## 3. Async Processing Strategy

### Decision: Celery with Redis Broker + WebSocket Progress Updates

**Rationale**:
- Celery provides mature task queue for Python ecosystem
- Redis broker offers low latency and persistence
- WebSocket enables real-time progress updates to frontend
- Achieves 1,000+ tracks/minute processing requirement
- Supports retry logic and error handling for reliability

**Alternatives Considered**:
- **Synchronous processing**: Rejected - blocks API for large uploads, violates <200ms response time
- **AWS SQS/Lambda**: Rejected - adds cloud vendor lock-in, complexity for local development
- **RabbitMQ broker**: Rejected - Redis simpler to operate, already used for caching

**Implementation Approach**:
- Celery worker pool with 4-8 workers (CPU-bound matching)
- Task priority queue: high priority for small catalogs, normal for large
- Progress tracking: update database every 100 tracks, emit WebSocket event
- Error handling: retry failed matches 3 times with exponential backoff
- Result storage: persist in PostgreSQL for audit trail

## 4. File Upload Security

### Decision: Basic Validation (Type, Size, Structure) - No Antivirus

**Rationale**:
- Clarification decision: Basic validation sufficient for MVP
- Validates file extensions against whitelist: `.csv`, `.xlsx`, `.json`, `.xml`
- Size limit enforcement: 500MB max
- Structural validation: Parse headers/schema before processing
- Lower complexity and operational overhead

**Alternatives Considered**:
- **Third-party antivirus integration (ClamAV)**: Deferred - adds latency, infrastructure complexity
- **Sandboxed execution**: Deferred - overkill for structured data files

**Implementation Approach**:
```python
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.xml'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

def validate_upload(file: UploadFile) -> None:
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format: {ext}")

    # Check size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)     # Reset
    if size > MAX_FILE_SIZE:
        raise HTTPException(413, "File exceeds 500MB limit")

    # Structural validation (parser-specific)
    parser = get_parser(ext)
    parser.validate_structure(file)
```

## 5. Frontend Performance Optimization

### Decision: Virtual Scrolling + Debounced Search + TanStack Query Caching

**Rationale**:
- **React Window**: Renders only visible rows, handles 10,000+ items smoothly
- **Debounced search**: Reduces API calls from 1-per-keystroke to 1-per-300ms pause
- **TanStack Query**: Automatic caching, background refetching, stale-while-revalidate
- Achieves <3 second page load, <1 second search response requirements

**Alternatives Considered**:
- **Server-side pagination only**: Rejected - poor UX for browsing, many page reloads
- **Load all data into memory**: Rejected - millions of works exceed browser memory limits
- **Custom virtualization**: Rejected - React Window is battle-tested, maintained

**Implementation Approach**:
```typescript
// Virtual scrolling for large tables
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={works.length}
  itemSize={50}
  overscanCount={5}
>
  {Row}
</FixedSizeList>

// Debounced search
const debouncedSearch = useDebounce(searchTerm, 300);

// TanStack Query with caching
const { data } = useQuery({
  queryKey: ['works', filters],
  queryFn: () => api.getWorks(filters),
  staleTime: 5 * 60 * 1000,  // 5 min
  cacheTime: 10 * 60 * 1000, // 10 min
});
```

## 6. Authentication & Session Management

### Decision: JWT Access Tokens + Refresh Tokens + Redis Session Store

**Rationale**:
- JWT access tokens (15min TTL): Stateless, no database lookup per request
- Refresh tokens (7 days TTL): Secure rotation without re-login
- Redis session store: Fast lookup, automatic expiration, supports logout
- Two-role model (Publisher, Admin) maps to JWT claims

**Alternatives Considered**:
- **Session cookies only**: Rejected - harder to scale horizontally, requires sticky sessions
- **OAuth2 with external provider**: Deferred to Phase 4 - adds integration complexity for MVP
- **Database session store**: Rejected - adds latency, database load

**Implementation Approach**:
```python
# JWT payload structure
{
  "sub": "user_id",
  "role": "publisher" | "admin",
  "exp": timestamp,
  "jti": "token_id"  # For revocation via Redis
}

# Refresh token rotation
1. Client sends refresh token
2. Validate refresh token signature and expiration
3. Check Redis blacklist (revoked tokens)
4. Issue new access token + new refresh token
5. Invalidate old refresh token in Redis
```

## 7. Duplicate Handling Strategy

### Decision: Merge Duplicates Before Matching with Metadata Combination

**Rationale**:
- Clarification decision: Merge strategy prevents duplicate processing
- Deduplication key: (title_normalized, artist_normalized, duration_bucket)
- Metadata merge: prefer non-null values, concatenate arrays
- Reduces processing time, improves result quality

**Alternatives Considered**:
- **Process all duplicates independently**: Rejected - wastes compute, confusing results
- **Skip duplicates after first**: Rejected - loses potentially valuable metadata from later entries

**Implementation Approach**:
```python
def merge_duplicates(tracks: List[Track]) -> List[Track]:
    merged = {}
    for track in tracks:
        key = (
            normalize_title(track.title),
            normalize_artist(track.artist),
            duration_bucket(track.duration, 10)  # 10-second buckets
        )

        if key in merged:
            # Merge metadata
            merged[key] = combine_metadata(merged[key], track)
        else:
            merged[key] = track

    return list(merged.values())
```

## 8. Multiple Match Display

### Decision: Show All Matches with Visual Ranking

**Rationale**:
- Clarification decision: Transparency over filtering
- Users see all possibilities, make informed decisions
- Visual ranking (color-coding, sorting) guides attention to best matches
- Supports edge cases where lower-ranked match might be correct

**Implementation Approach**:
```typescript
interface MatchDisplay {
  uploadedTrack: Track;
  matches: Array<{
    work: MusicalWork;
    score: number;
    confidence: 'high' | 'medium' | 'low';
    rank: number;
  }>;
}

// UI: Color-coded badges, sorted by score
<MatchResults>
  {matches
    .sort((a, b) => b.score - a.score)
    .map((match, idx) => (
      <MatchCard
        rank={idx + 1}
        confidence={match.confidence}
        score={match.score}
        work={match.work}
      />
    ))}
</MatchResults>
```

## Technology Stack Summary

### Backend
- **Framework**: FastAPI 0.118+ (async, auto-docs, Pydantic integration)
- **ORM**: SQLModel 0.0.25 (SQLAlchemy 2.0 + Pydantic)
- **Database**: PostgreSQL 15+ (ACID, advanced indexing)
- **Search**: Elasticsearch 8.x (full-text search)
- **Cache**: Redis 7.x (query cache, sessions, Celery broker)
- **Task Queue**: Celery 5.x (async processing)
- **Validation**: Pydantic v2 (fast, type-safe)
- **Testing**: pytest 8.x (async support, fixtures)

### Frontend
- **Framework**: React 19.1 (hooks, concurrent features)
- **Language**: TypeScript 5.9 (strict mode)
- **Build Tool**: Vite 7.1 (fast HMR, optimized builds)
- **State**: TanStack Query 5.x (server state), Zustand (UI state)
- **UI Library**: Ant Design 5.x or Material-UI 6.x (accessible components)
- **Virtualization**: React Window 1.8 (large lists)
- **Charts**: Recharts 2.x (dashboard visualizations)
- **Testing**: Vitest 2.x + React Testing Library

### Infrastructure
- **Containerization**: Docker + Docker Compose (dev environment)
- **Migrations**: Alembic (database schema versioning)
- **Process Manager**: Gunicorn with Uvicorn workers (production)
- **Reverse Proxy**: Nginx (static files, load balancing)

## Performance Validation Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Dashboard page load | <3s (95th percentile) | Lighthouse, Real User Monitoring |
| Search query response | <500ms (90th percentile) | API endpoint monitoring |
| Database query | <50ms (90th percentile) | PostgreSQL EXPLAIN ANALYZE |
| Catalog processing | 1,000+ tracks/min | Celery task metrics |
| Concurrent users | 100+ without degradation | Load testing (Locust/K6) |
| API error rate | <0.1% | Application logging, APM |
| System uptime | 99.9% | Uptime monitoring |

## Next Steps

1. **Phase 1**: Generate data models, API contracts, and failing tests
2. **Phase 2**: Create implementation tasks following TDD approach
3. **Phase 3-4**: Implement features per constitutional principles
4. **Phase 5**: Performance validation against criteria above

---

*Research completed: 2025-10-04*
*Ready for Phase 1: Design & Contracts*
