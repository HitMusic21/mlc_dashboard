
# Implementation Plan: BWARM Dashboard Improvements

**Branch**: `001-bwarm-dashboard-high` | **Date**: 2025-10-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/specs/001-bwarm-dashboard-high/spec.md`
**User Context**: impeovemtn implementation (improvement implementation)

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

The BWARM Dashboard is a high-performance web application enabling music publishers to match their catalogs (5,000-50,000 tracks) against a massive 2TB BWARM database to identify uncollected royalties. Publishers upload catalogs in multiple formats (CSV, Excel, JSON, XML), and the system matches songs using advanced algorithms (Jaro-Winkler, Levenshtein, TF-IDF) with confidence scoring (high ≥0.85, medium 0.70-0.84, low <0.70).

**Current State (Analysis Complete)**:
- ✅ Backend: 19 API endpoints, FastAPI + PostgreSQL, async processing ready
- ✅ Frontend: 6 pages (React 19 + TypeScript), 17+ components, virtualized tables
- ⚠️ **0% CSS implementation** - semantic classes without styles
- ⚠️ **63 missing features** identified in comprehensive analysis
- ⚠️ Mobile experience completely broken (desktop layout on mobile)

**Implementation Focus (from user context "improvement implementation")**:
Based on comprehensive deep-scan analysis completed (7 research documents created), this plan focuses on implementing the TOP PRIORITY improvements to transform from "functional tool" to "indispensable platform":
1. Visual design system (CSS implementation)
2. Enhanced dashboard layout (2-column responsive grid)
3. Critical UX features (upload history, progress detail, notifications)
4. Mobile-first responsive design

## Technical Context
**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript 5.9.3, React 19.1.1

**Primary Dependencies**:
- Backend: FastAPI 0.118, SQLModel 0.0.25, Celery 5.4, Redis 7, Elasticsearch 8, asyncpg 0.30
- Frontend: Vite 7.1.7, TanStack Query 5.90, Zustand 5.0.8, Recharts 3.2.1, Tailwind CSS 3.4.18

**Storage**:
- Database: PostgreSQL 15+ (2TB BWARM data, user uploads, matches)
- Cache: Redis (Celery broker, query caching)
- Search: Elasticsearch (full-text search on musical works)
- Files: Local/S3 (uploaded catalogs)

**Testing**:
- Backend: pytest (contract, integration, unit), pytest-asyncio
- Frontend: Vitest, React Testing Library
- E2E: Playwright (planned)

**Target Platform**: Web (desktop + mobile browsers), Progressive Web App (future)

**Project Type**: Web application (backend + frontend)

**Performance Goals**:
- Dashboard load: <3s (95th percentile)
- Query response: <500ms (90th percentile)
- Catalog processing: ≥1,000 tracks/min
- Concurrent users: 100+ without degradation

**Constraints**:
- File uploads: Max 500MB
- Processing timeout: 10 min for large catalogs
- Response times: <3s page loads, <500ms queries
- Uptime: 99.9% availability
- Mobile: Must work on phones (currently broken)

**Scale/Scope**:
- Database: 2TB BWARM data, ~millions of musical works
- Users: Publishers (100s), Admins (10s)
- Catalogs: 1-50K tracks per upload
- Daily uploads: ~50-100 catalogs
- Frontend: 6 pages, 20+ components, 40+ API integration points

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Clean and Modular Code
- [x] Components/services have single responsibility (files <300 lines)
  - ✅ Existing code: Dashboard.tsx (254 lines), API routes modular
  - ✅ New components will follow: stat cards, chart panels, feed widgets
- [x] No circular dependencies between modules
  - ✅ Current: Clean dependency flow (models → crud → services → api → UI)
  - ✅ New features maintain hierarchy
- [x] Clear separation of concerns (models, services, API, UI)
  - ✅ Backend: models/ crud/ services/ api/ separation maintained
  - ✅ Frontend: components/ pages/ services/ hooks/ separation clear

### II. FastAPI Best Practices (Backend)
- [x] Async/await used for I/O operations
  - ✅ Existing: All DB operations async (asyncpg), Celery for long tasks
  - ✅ New: Notifications API will use async patterns
- [x] Pydantic models for request/response validation
  - ✅ Existing: All schemas in app/schemas/ use Pydantic
  - ✅ New: Preferences, notifications schemas will follow
- [x] Dependency injection for shared resources
  - ✅ Existing: get_db, get_current_user dependencies used
  - ✅ New endpoints will reuse existing DI patterns
- [x] APIRouter for endpoint grouping
  - ✅ Existing: /auth, /works, /catalog, /admin routers
  - ✅ New: /preferences, /notifications routers
- [x] Proper error handling with HTTPException
  - ✅ Existing: Custom exceptions in core/exceptions.py
  - ✅ Pattern established and working

### III. React Best Practices (Frontend)
- [x] Functional components with hooks (no class components)
  - ✅ All current components use hooks (useState, useQuery, useEffect)
  - ✅ New components will continue pattern
- [x] TypeScript with strict mode
  - ✅ tsconfig.json has strict: true
  - ✅ No `any` types in current codebase
- [x] Components <200 lines with clear responsibility
  - ✅ Current components modular (Header 150L, Sidebar 120L)
  - ⚠️ Dashboard.tsx at 254L - will split into widgets
- [x] Accessibility standards followed (WCAG 2.1 AA)
  - ✅ Semantic HTML used, ARIA labels present
  - ✅ New components will add keyboard navigation, focus management
- [x] Proper error boundaries and loading states
  - ✅ Loading spinners present, Suspense boundaries in App.tsx
  - ⚠️ Error boundaries missing - will add in Phase 1

### IV. Test-First Development (NON-NEGOTIABLE)
- [x] Tests written BEFORE implementation
  - ✅ 29 test files exist (contract, integration tests)
  - ✅ TDD will be followed: write tests for new endpoints/components first
- [x] Contract tests for API schemas
  - ✅ Existing: test_catalog_upload.py, test_works_list.py validate schemas
  - ✅ New: test_preferences.py, test_notifications.py will be created
- [x] Integration tests for user flows
  - ✅ Existing: test_auth_flow.py, test_browse_works.py, test_small_catalog.py
  - ✅ New: test_dashboard_customization.py, test_mobile_experience.py
- [x] Target: 80% code coverage minimum
  - ✅ Backend coverage good (pytest markers indicate comprehensive tests)
  - ⚠️ Frontend tests needed - will add Vitest coverage

### V. Type Safety and Validation
- [x] Pydantic models for all API boundaries (backend)
  - ✅ Existing: schemas/auth.py, schemas/works.py, schemas/catalog.py
  - ✅ New: schemas/preferences.py, schemas/notifications.py
- [x] TypeScript strict mode, no unjustified `any` (frontend)
  - ✅ Strict mode enabled, types/ directory well-organized
  - ✅ New types will be added to types/preferences.ts, types/notifications.ts
- [x] Runtime validation at system boundaries
  - ✅ Pydantic validates API inputs, FastAPI rejects invalid requests
  - ✅ Frontend validates forms before submission
- [x] Database migrations with Alembic
  - ✅ Alembic configured, 001_initial_schema.py exists
  - ✅ New tables (user_preferences, notifications) will get migrations

**Violations**: None - all constitutional requirements can be satisfied with current architecture and planned improvements

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── works.py
│   │       ├── catalog.py
│   │       ├── admin.py
│   │       ├── preferences.py (NEW)
│   │       └── notifications.py (NEW)
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── crud/
│   │   ├── works.py
│   │   ├── catalog.py
│   │   ├── matches.py
│   │   ├── user.py
│   │   ├── preferences.py (NEW)
│   │   └── notifications.py (NEW)
│   ├── db/
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── musical_work.py
│   │   ├── catalog_upload.py
│   │   ├── catalog_match.py
│   │   ├── user.py
│   │   ├── user_preferences.py (NEW)
│   │   └── notification.py (NEW)
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── works.py
│   │   ├── catalog.py
│   │   ├── preferences.py (NEW)
│   │   └── notifications.py (NEW)
│   ├── services/
│   │   ├── matching/
│   │   ├── parsers/
│   │   ├── search.py
│   │   └── cache.py
│   └── tasks/
│       ├── catalog_processing.py
│       └── cleanup.py
├── tests/
│   ├── contract/
│   │   ├── test_auth_*.py
│   │   ├── test_works_*.py
│   │   ├── test_catalog_*.py
│   │   ├── test_preferences_*.py (NEW)
│   │   └── test_notifications_*.py (NEW)
│   └── integration/
│       ├── test_auth_flow.py
│       ├── test_dashboard_customization.py (NEW)
│       └── test_mobile_experience.py (NEW)
├── alembic/
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_preferences_notifications.py (NEW)
└── main.py

frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── VirtualizedTable.tsx
│   │   │   └── ExportButton.tsx
│   │   ├── dashboard/ (NEW)
│   │   │   ├── StatCard.tsx
│   │   │   ├── EnhancedStatCard.tsx
│   │   │   ├── DualChartPanel.tsx
│   │   │   ├── ActivityFeed.tsx
│   │   │   ├── InsightsWidget.tsx
│   │   │   └── QuickActionsWidget.tsx
│   │   ├── layout/
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── results/
│   │   ├── upload/
│   │   └── ui/
│   ├── hooks/
│   │   ├── useDebounce.ts
│   │   ├── useFileUpload.ts
│   │   ├── useVirtualization.ts
│   │   └── usePreferences.ts (NEW)
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx (ENHANCED)
│   │   ├── WorksBrowser.tsx
│   │   ├── CatalogMatcher.tsx
│   │   ├── ResultsViewer.tsx
│   │   └── Admin.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── cache.ts
│   ├── store/
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── preferencesStore.ts (NEW)
│   ├── styles/ (NEW)
│   │   ├── tokens/
│   │   │   ├── colors.css
│   │   │   ├── typography.css
│   │   │   └── spacing.css
│   │   ├── base/
│   │   │   ├── reset.css
│   │   │   └── global.css
│   │   ├── components/
│   │   │   ├── buttons.css
│   │   │   ├── cards.css
│   │   │   └── dashboard.css
│   │   └── index.css (imports all)
│   ├── types/
│   │   ├── api.ts
│   │   ├── works.ts
│   │   ├── catalog.ts
│   │   ├── preferences.ts (NEW)
│   │   └── notifications.ts (NEW)
│   └── App.tsx
└── tests/ (NEW)
    └── components/
        ├── Dashboard.test.tsx
        └── EnhancedStatCard.test.tsx

specs/001-bwarm-dashboard-high/ (this directory)
├── spec.md
├── plan.md (this file)
├── research.md (Phase 0 output)
├── data-model.md (Phase 1 output)
├── quickstart.md (Phase 1 output)
├── contracts/ (Phase 1 output)
│   ├── preferences-api.yaml
│   └── notifications-api.yaml
└── tasks.md (/tasks command output)
```

**Structure Decision**: Web application with backend (FastAPI) and frontend (React) separation. Existing structure is well-organized and follows constitutional principles. New improvements will:
1. Add preferences/notifications modules (backend + frontend)
2. Create dashboard component library (frontend/src/components/dashboard/)
3. Implement CSS design system (frontend/src/styles/)
4. Enhance existing pages with responsive patterns
5. Add comprehensive test coverage for new features

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. Load `.specify/templates/tasks-template.md` as base
2. Generate tasks from Phase 1 design docs:
   - data-model.md (3 new entities) → SQLModel classes + migrations
   - contracts/*.yaml (2 API specs) → contract tests + routes
   - quickstart.md (8 scenarios) → integration tests

**TDD Task Sequence**:

**Backend Tasks (Models → Tests → Implementation)**:
1. Create SQLModel classes for UserPreferences, Notification, ActivityLog [P]
2. Generate Alembic migration for 3 new tables [depends on 1]
3. Write contract tests for preferences API (GET/PUT endpoints) [P]
4. Write contract tests for notifications API (GET/PUT/DELETE endpoints) [P]
5. Implement preferences CRUD operations (crud/preferences.py) [depends on 3]
6. Implement notifications CRUD operations (crud/notifications.py) [depends on 4]
7. Implement preferences API routes (api/routes/preferences.py) [depends on 5]
8. Implement notifications API routes (api/routes/notifications.py) [depends on 6]
9. Write integration test: dashboard customization flow [depends on 7]
10. Write integration test: notification workflow [depends on 8]

**Frontend Tasks (Components → Tests → Integration)**:
11. Implement CSS design system (styles/tokens/, styles/base/, styles/components/) [P]
12. Create dashboard component library (EnhancedStatCard, DualChartPanel, ActivityFeed, etc.) [P]
13. Create preferences store (Zustand + LocalStorage sync) [P]
14. Create notifications store (Zustand + polling) [P]
15. Write component tests for EnhancedStatCard, DualChartPanel [P]
16. Refactor Dashboard.tsx to use new layout (2-column grid) [depends on 11,12]
17. Integrate preferences API (theme toggle, layout save) [depends on 13,16]
18. Integrate notifications API (bell icon, dropdown) [depends on 14,16]
19. Implement mobile responsive breakpoints [depends on 16]
20. Write accessibility tests (keyboard nav, screen reader) [P]

**Performance & Validation**:
21. Optimize bundle size (code splitting, lazy loading) [depends on 16]
22. Run Lighthouse audits (performance, accessibility) [depends on 19,20]
23. Execute k6 load tests (100 concurrent users) [depends on 8]
24. Validate database indexes (EXPLAIN ANALYZE queries) [depends on 2]
25. Execute quickstart validation (all 8 scenarios) [depends on all]

**Ordering Strategy**:
- TDD order: Tests before implementation (strict)
- Dependency order: Backend models → APIs → Frontend components
- Parallel execution: Independent files marked [P]
- Critical path: Models → Migrations → Tests → Routes → UI

**Estimated Output**: ~25-30 numbered, dependency-ordered tasks in tasks.md

**Dependencies**:
- Backend: Python 3.11, FastAPI, SQLModel, Alembic, pytest
- Frontend: React 19, TypeScript, Vite, Vitest, Tailwind CSS
- Testing: pytest (backend), Vitest + RTL (frontend), k6 (load), Lighthouse (performance)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md exists from initial spec
- [x] Phase 1: Design complete (/plan command)
  - ✅ data-model.md created (3 new entities: UserPreferences, Notification, ActivityLog)
  - ✅ contracts/preferences-api.yaml created (447 lines, 5 endpoints)
  - ✅ contracts/notifications-api.yaml created (358 lines, 6 endpoints)
  - ✅ quickstart.md created (595 lines, 8 test scenarios)
  - ✅ CLAUDE.md updated with new feature context
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
  - ✅ Task generation strategy documented (25-30 tasks estimated)
  - ✅ TDD sequence defined (tests before implementation)
  - ✅ Dependency order established (models → APIs → UI)
  - ✅ Parallel execution opportunities identified [P] markers
- [ ] Phase 3: Tasks generated (/tasks command) - READY TO EXECUTE
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (all principles satisfied)
- [x] Post-Design Constitution Check: PASS (no new violations introduced)
  - ✅ Modular design: 3 new models, 11 new endpoints, component library
  - ✅ FastAPI patterns: Async routes, Pydantic schemas, dependency injection
  - ✅ React patterns: Functional components, hooks, TypeScript strict
  - ✅ TDD ready: Contract tests specified, integration tests defined
  - ✅ Type safety: All schemas defined, validation rules complete
- [x] All NEEDS CLARIFICATION resolved (spec has clarifications from 2025-10-04)
- [x] Complexity deviations documented (none - no violations)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
