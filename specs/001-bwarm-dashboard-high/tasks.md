# Tasks: BWARM Dashboard Improvements

**Input**: Design documents from `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/specs/001-bwarm-dashboard-high/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md, UI_DESIGN_AUDIT.md, DASHBOARD_DESIGN_RECOMMENDATIONS.md
**Branch**: `001-bwarm-dashboard-high`
**Feature**: Dashboard UI/UX improvements (CSS design system, enhanced layout, preferences, notifications, mobile optimization)
**Context**: Backend 95% complete, frontend functional but lacks CSS. Adding visual polish, new features, and mobile experience.

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: tech stack (FastAPI, React 19, PostgreSQL, existing 95% complete backend)
   → Focus: Dashboard improvements - visual design, UX, mobile
2. Load design documents:
   → data-model.md: 3 NEW entities (UserPreferences, Notification, ActivityLog)
   → contracts/: 2 NEW API specs (preferences-api.yaml, notifications-api.yaml) with 11 endpoints
   → quickstart.md: 8 validation scenarios for improvements
   → UI_DESIGN_AUDIT.md: Complete CSS design system specification
   → DASHBOARD_DESIGN_RECOMMENDATIONS.md: Layout restructuring patterns
3. Generate tasks by category with TDD ordering
   → Backend: Models → Tests → CRUD → Routes (3 new tables, 11 new endpoints)
   → Frontend: CSS → Components → State → Integration (design system, dashboard widgets)
4. Apply parallelization rules (different files = [P])
5. Number tasks sequentially (T001, T002...)
6. Validate: All improvements align with constitutional principles (TDD, type safety, modularity)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/` at repository root
- **Frontend**: `frontend/` at repository root
- **Tests**: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Backend Foundation for New Features

### Database Models (SQLModel)
- [x] **T001** [P] UserPreferences model in `backend/app/models/user_preferences.py`
  - SQLModel class with fields: id (UUID), user_id (FK to User), dashboard_layout (JSONB), saved_searches (JSONB), theme (enum: light/dark/auto), items_per_page (10-200), notification_email (bool), notification_push (bool), language (ISO 639-1), timezone (IANA), created_at, updated_at
  - Validation: theme enum, items_per_page range, ISO codes
  - Unique constraint on user_id (one preference per user)
  - Index on user_id for fast lookup

- [x] **T002** [P] Notification model in `backend/app/models/notification.py`
  - SQLModel class with fields: id (UUID), user_id (FK to User), type (enum: info/success/warning/error), title (max 200 chars), message (max 1000 chars), related_entity_type (nullable), related_entity_id (UUID nullable), severity (enum: low/medium/high/critical), is_read (bool default False), action_url (nullable), created_at, read_at (nullable)
  - Composite index on (user_id, is_read, created_at DESC) for efficient unread queries
  - Index on created_at for cleanup operations

- [x] **T003** [P] ActivityLog model in `backend/app/models/activity_log.py`
  - SQLModel class with fields: id (UUID), user_id (FK to User nullable), action (format: "{entity}.{verb}"), entity_type (nullable), entity_id (UUID nullable), description (max 500 chars), metadata (JSONB), ip_address (inet), user_agent (max 500 chars), status (enum: success/failure/partial), created_at
  - Action examples: "catalog.upload", "work.search", "user.login"
  - Index on user_id, action, created_at for analytics queries
  - Composite index (entity_type, entity_id) for entity history

- [x] **T004** Generate Alembic migration for new models
  - Run: `cd backend && alembic revision --autogenerate -m "Add user preferences, notifications, and activity log"`
  - Review migration for correct indexes
  - Test: `alembic upgrade head` and verify tables created
  - Test: `alembic downgrade -1` and verify rollback

### Pydantic Schemas
- [x] **T005** [P] Preferences schemas in `backend/app/schemas/preferences.py`
  - UserPreferencesResponse, UserPreferencesUpdate
  - DashboardLayoutConfig (typing for JSONB field)
  - SavedSearchSchema (typing for saved searches array)

- [x] **T006** [P] Notification schemas in `backend/app/schemas/notifications.py`
  - NotificationResponse, NotificationCreate
  - NotificationListResponse with pagination
  - UnreadCountResponse

- [x] **T007** [P] Activity log schemas in `backend/app/schemas/activity.py`
  - ActivityLogResponse, ActivityLogCreate
  - ActivityStatsResponse (for dashboard widget)

### Contract Tests (TDD - Must Fail First)
- [x] **T008** [P] Contract test for GET /api/v1/preferences in `backend/tests/contract/test_preferences_get.py`
  - Test response 200 schema: UserPreferencesResponse
  - Test response 401 without auth token
  - Test default preferences returned if none exist

- [x] **T009** [P] Contract test for PUT /api/v1/preferences in `backend/tests/contract/test_preferences_update.py`
  - Test request schema: UserPreferencesUpdate (partial updates)
  - Test response 200 schema: UserPreferencesResponse
  - Test validation errors for invalid theme/items_per_page

- [ ] **T010** [P] Contract test for POST /api/v1/preferences/layout in `backend/tests/contract/test_preferences_layout.py`
  - Test request schema: {"layout": JSONB}
  - Test response 200 with updated preferences
  - Test JSONB validation

- [ ] **T011** [P] Contract test for POST /api/v1/preferences/searches in `backend/tests/contract/test_preferences_save_search.py`
  - Test request schema: {"name": str, "filters": dict}
  - Test response 201 with saved search added to array
  - Test duplicate name handling

- [ ] **T012** [P] Contract test for DELETE /api/v1/preferences/searches/{id} in `backend/tests/contract/test_preferences_delete_search.py`
  - Test response 204 for successful delete
  - Test response 404 for non-existent search

- [x] **T013** [P] Contract test for GET /api/v1/notifications in `backend/tests/contract/test_notifications_list.py`
  - Test response 200 schema: NotificationListResponse with pagination
  - Test query params: page, limit, is_read, severity
  - Test ordering: unread first, then by created_at DESC

- [x] **T014** [P] Contract test for GET /api/v1/notifications/unread-count in `backend/tests/contract/test_notifications_count.py`
  - Test response 200 schema: {"count": int}
  - Test only counts unread for current user

- [ ] **T015** [P] Contract test for PUT /api/v1/notifications/{id}/read in `backend/tests/contract/test_notifications_mark_read.py`
  - Test response 200 with is_read=true, read_at timestamp
  - Test response 404 for non-existent notification

- [ ] **T016** [P] Contract test for PUT /api/v1/notifications/read-all in `backend/tests/contract/test_notifications_read_all.py`
  - Test response 200 with count of marked notifications
  - Test only marks current user's notifications

- [ ] **T017** [P] Contract test for DELETE /api/v1/notifications/{id} in `backend/tests/contract/test_notifications_delete.py`
  - Test response 204 for successful delete
  - Test response 403 if not owner

- [ ] **T018** [P] Contract test for DELETE /api/v1/notifications/clear-read in `backend/tests/contract/test_notifications_clear.py`
  - Test response 200 with count of deleted notifications
  - Test only deletes read notifications for current user

### CRUD Operations
- [ ] **T019** [P] Preferences CRUD in `backend/app/crud/preferences.py`
  - async def get_preferences(session, user_id) → UserPreferences | None
  - async def upsert_preferences(session, user_id, data) → UserPreferences
  - async def update_layout(session, user_id, layout) → UserPreferences
  - async def add_saved_search(session, user_id, search) → UserPreferences
  - async def remove_saved_search(session, user_id, search_id) → UserPreferences

- [ ] **T020** [P] Notifications CRUD in `backend/app/crud/notifications.py`
  - async def create_notification(session, user_id, data) → Notification
  - async def get_notifications(session, user_id, filters, pagination) → List[Notification]
  - async def get_unread_count(session, user_id) → int
  - async def mark_as_read(session, notification_id, user_id) → Notification
  - async def mark_all_read(session, user_id) → int
  - async def delete_notification(session, notification_id, user_id) → bool
  - async def clear_read_notifications(session, user_id) → int

- [ ] **T021** [P] Activity log CRUD in `backend/app/crud/activity.py`
  - async def log_activity(session, user_id, action, entity_type, entity_id, description, metadata, ip, user_agent, status) → ActivityLog
  - async def get_recent_activity(session, user_id, limit) → List[ActivityLog]
  - async def get_activity_stats(session, user_id) → dict

### API Routes
- [ ] **T022** Preferences routes in `backend/app/api/routes/preferences.py`
  - GET /: Get current user preferences (or defaults)
  - PUT /: Update preferences (partial)
  - POST /layout: Update dashboard layout
  - POST /searches: Add saved search
  - DELETE /searches/{id}: Remove saved search
  - Depend on get_current_active_user

- [ ] **T023** Notifications routes in `backend/app/api/routes/notifications.py`
  - GET /: List notifications with pagination
  - GET /unread-count: Get unread count
  - PUT /{id}/read: Mark as read
  - PUT /read-all: Mark all as read
  - DELETE /{id}: Delete notification
  - DELETE /clear-read: Clear all read
  - Depend on get_current_active_user

- [ ] **T024** Update main.py to include new routes
  - Import preferences_router, notifications_router
  - Include routers with prefix /api/v1
  - Update OpenAPI metadata with new endpoints

### Activity Logging Integration
- [ ] **T025** Activity logging middleware in `backend/app/api/middleware/activity_logger.py`
  - Middleware to automatically log API requests
  - Extract user_id, action, IP, user-agent
  - Log on response with success/failure status
  - Exclude health check and static endpoints

- [ ] **T026** Update existing routes to emit notifications
  - catalog.py: Create notification on upload complete/failed
  - works.py: Create notification on saved search results ready
  - Integration with notification CRUD

---

## Phase 2: CSS Design System Implementation

### Design Tokens & Global Styles
- [ ] **T027** Create CSS design tokens in `frontend/src/styles/tokens.css`
  - CSS custom properties from UI_DESIGN_AUDIT.md
  - Color palette: primary (indigo 600), secondary (purple 600), accent (pink 500), success/warning/error/info
  - Light/dark mode color schemes
  - Typography scale (12px to 48px)
  - Spacing grid (0.5rem to 12rem, 8px base)
  - Shadow system (sm/md/lg/xl/2xl)
  - Border radius (sm/md/lg/full)
  - Transition durations (fast/base/slow)

- [ ] **T028** Global CSS reset and base styles in `frontend/src/styles/global.css`
  - CSS reset (margin/padding normalization)
  - Box-sizing: border-box
  - Body font-family: Inter var (with system fallbacks)
  - Color scheme: light/dark detection
  - Smooth scrolling
  - Focus-visible outline styles

- [ ] **T029** [P] Typography utilities in `frontend/src/styles/typography.css`
  - Heading classes (h1-h6) with responsive sizing
  - Body text classes (body-lg, body-base, body-sm)
  - Font weight utilities (light/normal/medium/semibold/bold)
  - Text color utilities using design tokens
  - Line-height utilities

- [ ] **T030** [P] Layout utilities in `frontend/src/styles/layout.css`
  - Container classes (container-sm/md/lg/xl/2xl)
  - Grid system (grid-cols-1 to 12)
  - Flexbox utilities (flex-row/col, justify-*, items-*, gap-*)
  - Spacing utilities (p-*, m-*, space-y-*, space-x-*)
  - Responsive breakpoint classes (sm:, md:, lg:, xl:, 2xl:)

- [ ] **T031** [P] Component base styles in `frontend/src/styles/components.css`
  - Button variants (primary/secondary/ghost/danger)
  - Input/textarea/select base styles
  - Card/panel base styles
  - Badge/tag base styles
  - Modal/dialog base styles
  - Dropdown/menu base styles
  - Table base styles

- [ ] **T032** Dark mode implementation in `frontend/src/hooks/useDarkMode.ts`
  - Hook to toggle dark mode
  - Persist preference in localStorage
  - Sync with UserPreferences API
  - Apply .dark class to document root
  - Media query detection for system preference

---

## Phase 3: Enhanced Dashboard Components

### Dashboard Widgets (New Components)
- [ ] **T033** StatCard component in `frontend/src/components/dashboard/StatCard.tsx`
  - Props: title, value, trend (up/down/neutral), trendValue, icon, onClick
  - Visual design from DASHBOARD_DESIGN_RECOMMENDATIONS.md
  - Sparkline mini-chart using Recharts (optional)
  - Trend indicator with arrow and percentage
  - Hover effect with scale transform
  - Loading skeleton state
  - TypeScript interface for props

- [ ] **T034** [P] DualChartPanel component in `frontend/src/components/dashboard/DualChartPanel.tsx`
  - Side-by-side chart layout (AreaChart + BarChart)
  - Left: Monthly upload trend (AreaChart)
  - Right: Match confidence distribution (BarChart)
  - Responsive: stack on mobile
  - Uses Recharts with custom colors from design tokens
  - Loading state with animated placeholder

- [ ] **T035** [P] ActivityFeed component in `frontend/src/components/dashboard/ActivityFeed.tsx`
  - Display recent activity log entries
  - Virtualized list for performance (react-window)
  - Activity icons based on action type
  - Relative timestamps ("2 minutes ago")
  - Click to view related entity
  - Real-time updates via polling (every 30s)

- [ ] **T036** [P] NotificationBadge component in `frontend/src/components/common/NotificationBadge.tsx`
  - Bell icon with unread count badge
  - Animated pulse when new notifications
  - Click to open NotificationDropdown
  - Position: absolute in header
  - Accessibility: ARIA live region

- [ ] **T037** [P] NotificationDropdown component in `frontend/src/components/common/NotificationDropdown.tsx`
  - Dropdown panel with notification list
  - Mark as read button (individual & all)
  - Clear read button
  - Severity color coding
  - Link to full notifications page
  - Max height with scroll
  - Click outside to close

- [ ] **T038** [P] SavedSearchPanel component in `frontend/src/components/dashboard/SavedSearchPanel.tsx`
  - Display user's saved searches
  - Quick execute button per search
  - Edit/delete actions
  - Collapsible panel
  - Empty state: "No saved searches yet"

### Dashboard Layout Restructure
- [ ] **T039** Enhanced Dashboard page in `frontend/src/pages/Dashboard.tsx`
  - Implement 2-column grid layout from DASHBOARD_DESIGN_RECOMMENDATIONS.md
  - Left column (60%): DualChartPanel, ActivityFeed
  - Right column (40%): 4 StatCards (stacked), SavedSearchPanel
  - Responsive: single column on mobile
  - Use TanStack Query for data fetching with 5min cache
  - Loading states for all widgets
  - Error boundaries per widget

- [ ] **T040** Update Header component in `frontend/src/components/layout/Header.tsx`
  - Add NotificationBadge to right side
  - Add theme toggle button (sun/moon icon)
  - Add user avatar with preferences dropdown
  - Responsive: hamburger menu on mobile
  - Sticky position on scroll

---

## Phase 4: User Preferences Integration

### Frontend Services & State
- [ ] **T041** Preferences API service in `frontend/src/services/preferencesApi.ts`
  - getPreferences() → UserPreferences
  - updatePreferences(data) → UserPreferences
  - updateLayout(layout) → UserPreferences
  - addSavedSearch(search) → UserPreferences
  - removeSavedSearch(id) → UserPreferences
  - Uses axios with auth headers

- [ ] **T042** Preferences store in `frontend/src/stores/preferencesStore.ts`
  - Zustand store for preferences state
  - State: preferences, isLoading, error
  - Actions: fetchPreferences, updatePreferences, setTheme, setItemsPerPage, addSavedSearch, removeSavedSearch
  - Sync to backend on changes
  - Sync to localStorage for offline access

- [ ] **T043** PreferencesModal component in `frontend/src/components/settings/PreferencesModal.tsx`
  - Modal dialog for user settings
  - Tabs: General, Display, Notifications, Advanced
  - General: language, timezone
  - Display: theme, items per page, dashboard layout
  - Notifications: email/push toggles
  - Advanced: export data, clear cache
  - Save/Cancel buttons
  - Form validation

- [ ] **T044** Dashboard layout customization in `frontend/src/components/dashboard/DashboardLayoutEditor.tsx`
  - Drag-and-drop grid layout using react-grid-layout
  - Add/remove widgets
  - Resize widgets
  - Save custom layout to preferences
  - Reset to default layout
  - Preview mode

- [ ] **T045** Apply preferences throughout app
  - Use preferencesStore in all components
  - Apply items_per_page to pagination
  - Apply theme to document root
  - Apply dashboard_layout to Dashboard page
  - Load saved searches in WorksBrowser

---

## Phase 5: Notifications System

### Frontend Integration
- [ ] **T046** Notifications API service in `frontend/src/services/notificationsApi.ts`
  - getNotifications(params) → NotificationListResponse
  - getUnreadCount() → number
  - markAsRead(id) → Notification
  - markAllAsRead() → count
  - deleteNotification(id) → void
  - clearReadNotifications() → count

- [ ] **T047** Notifications store in `frontend/src/stores/notificationsStore.ts`
  - Zustand store for notifications state
  - State: notifications, unreadCount, isLoading
  - Actions: fetchNotifications, fetchUnreadCount, markAsRead, markAllAsRead, deleteNotification
  - Auto-refresh unread count every minute
  - WebSocket listener for real-time notifications (optional)

- [ ] **T048** NotificationsPage component in `frontend/src/pages/Notifications.tsx`
  - Full-page notifications view
  - Filter by: all/unread, severity
  - Sort by: date
  - Mark as read on click
  - Bulk actions: mark all read, clear read
  - Pagination for old notifications
  - Empty state: "No notifications"

- [ ] **T049** Toast notification system in `frontend/src/components/common/Toast.tsx`
  - Toast container component
  - Auto-dismiss after 5 seconds (configurable)
  - Severity variants: info/success/warning/error
  - Close button
  - Stack multiple toasts
  - Animation: slide in from top-right
  - Accessibility: ARIA live region

- [ ] **T050** Integrate notifications into app workflow
  - Show toast on catalog upload complete
  - Show toast on search results ready
  - Show toast on API errors
  - Update NotificationBadge on new notifications
  - Add route for /notifications page

---

## Phase 6: Mobile Optimization

### Responsive Design
- [ ] **T051** Mobile navigation in `frontend/src/components/layout/MobileNav.tsx`
  - Slide-out drawer navigation
  - Hamburger menu button in header
  - Swipe to close gesture
  - Overlay backdrop
  - Smooth animation
  - Touch-friendly tap targets (min 44px)

- [ ] **T052** Mobile-optimized table in `frontend/src/components/common/MobileTable.tsx`
  - Card-based layout for mobile
  - Stacked rows instead of columns
  - Swipe actions (delete, view)
  - Infinite scroll instead of pagination
  - Pull-to-refresh
  - Falls back to VirtualizedTable on desktop

- [ ] **T053** Touch gesture handlers in `frontend/src/hooks/useSwipe.ts`
  - Hook for swipe detection (left/right/up/down)
  - Configurable threshold
  - Velocity calculation
  - Prevent scroll during swipe
  - Return: onTouchStart, onTouchMove, onTouchEnd handlers

- [ ] **T054** Mobile upload flow in `frontend/src/components/upload/MobileUploader.tsx`
  - Full-screen upload interface on mobile
  - Large drop zone
  - Camera integration for photo uploads (future)
  - Simplified form (fewer fields)
  - Step-by-step wizard
  - Progress bar prominent

- [ ] **T055** Responsive dashboard for mobile
  - Update Dashboard.tsx with mobile-specific layout
  - Single column on mobile
  - Collapsible widgets
  - Swipe between widget tabs
  - Sticky filters on scroll
  - Bottom navigation bar (alternative)

- [ ] **T056** Mobile performance optimizations
  - Lazy load images with placeholder
  - Reduce initial bundle size (code splitting)
  - Optimize font loading (font-display: swap)
  - Service worker for offline support (optional)
  - Viewport meta tag with proper scaling

---

## Phase 7: Integration Tests for New Features

### Integration Tests
- [ ] **T057** [P] Integration test for Validation Scenario 1: Visual Design System in `frontend/tests/integration/test_design_system.spec.ts`
  - Test CSS tokens loaded correctly
  - Test dark mode toggle works
  - Test all color variables accessible
  - Test typography scales applied
  - Test component styles render correctly

- [ ] **T058** [P] Integration test for Validation Scenario 2: Enhanced Dashboard Layout in `frontend/tests/integration/test_dashboard_layout.spec.ts`
  - Test 2-column grid on desktop
  - Test single column on mobile
  - Test StatCards display with trends
  - Test DualChartPanel renders charts
  - Test ActivityFeed shows recent activity
  - Test responsive breakpoints work

- [ ] **T059** [P] Integration test for Validation Scenario 3: Enhanced Stat Cards in `frontend/tests/integration/test_stat_cards.spec.ts`
  - Test trends display (up/down arrows)
  - Test sparklines render
  - Test drill-down navigation on click
  - Test loading states
  - Test real-time updates

- [ ] **T060** [P] Integration test for Validation Scenario 4: User Preferences in `backend/tests/integration/test_preferences_flow.py`
  - Test create default preferences on first login
  - Test update theme preference
  - Test save dashboard layout
  - Test add/remove saved search
  - Test preferences persist across sessions
  - Test LocalStorage + backend sync

- [ ] **T061** [P] Integration test for Validation Scenario 5: Real-Time Activity Feed in `frontend/tests/integration/test_activity_feed.spec.ts`
  - Test activity feed displays recent actions
  - Test polling updates feed (30s interval)
  - Test WebSocket updates (if implemented)
  - Test click to view related entity
  - Test virtualization for long lists

- [ ] **T062** [P] Integration test for Validation Scenario 6: Notification System in `backend/tests/integration/test_notifications_flow.py`
  - Test create notification on catalog complete
  - Test notification badge shows unread count
  - Test notification dropdown displays list
  - Test mark as read updates count
  - Test mark all as read
  - Test clear read notifications
  - Test toast notifications appear

- [ ] **T063** [P] Integration test for Validation Scenario 7: Mobile Experience in `frontend/tests/integration/test_mobile.spec.ts`
  - Test mobile navigation drawer
  - Test touch targets ≥44px
  - Test swipe gestures work
  - Test responsive layouts
  - Test page load < 3s on mobile network (throttled)
  - Test no horizontal scroll on any screen size

- [ ] **T064** [P] Integration test for Validation Scenario 8: Accessibility in `frontend/tests/integration/test_accessibility.spec.ts`
  - Test keyboard navigation (Tab, Enter, Esc)
  - Test screen reader labels (ARIA)
  - Test color contrast ratios (WCAG AA)
  - Test focus indicators visible
  - Test form validation errors announced
  - Run axe-core audit, assert 0 violations

---

## Phase 8: Performance Validation

### Performance Testing
- [ ] **T065** Frontend performance audit
  - Run Lighthouse on Dashboard page
  - Target scores: Performance ≥90, Accessibility ≥95, Best Practices ≥90, SEO ≥90
  - Measure page load time < 3s
  - Measure Time to Interactive < 5s
  - Verify no layout shifts (CLS < 0.1)
  - Optimize images (WebP format, lazy loading)

- [ ] **T066** API performance benchmarking with k6
  - Load test script in `backend/tests/performance/load_test.js`
  - Test 100 concurrent users (VUs)
  - Test endpoints: GET /works, GET /notifications, POST /preferences
  - Assert p95 response time < 500ms
  - Assert error rate < 0.1%
  - Monitor database connection pool usage
  - Generate HTML report

- [ ] **T067** Database query performance analysis
  - Run EXPLAIN ANALYZE on all new queries (preferences, notifications, activity)
  - Verify indexes are used (no sequential scans on large tables)
  - Check query execution time < 50ms
  - Monitor connection pool saturation
  - Add query result caching for expensive operations

- [ ] **T068** Frontend bundle size optimization
  - Analyze bundle with vite-bundle-visualizer
  - Target: main bundle < 200KB gzipped
  - Implement code splitting for routes
  - Lazy load heavy libraries (Recharts, react-window)
  - Tree-shake unused CSS
  - Use dynamic imports for modals/dialogs

---

## Phase 9: Documentation & Polish

### Documentation
- [ ] **T069** Update API documentation
  - Add OpenAPI specs for new endpoints (preferences, notifications)
  - Update Swagger UI examples
  - Document request/response schemas
  - Add authentication requirements
  - Update /docs endpoint

- [ ] **T070** Create user guide in `docs/USER_GUIDE.md`
  - Dashboard overview with screenshots
  - How to customize dashboard layout
  - How to save searches
  - How to manage notifications
  - How to change preferences
  - Mobile app usage tips
  - Accessibility features

- [ ] **T071** Update README.md
  - Add new features section (preferences, notifications, activity log)
  - Update screenshots with new dashboard design
  - Document CSS design system
  - Add mobile optimization details
  - Update architecture diagram with new models

- [ ] **T072** Create QUICKSTART.md validation checklist
  - 8 validation scenarios from quickstart.md
  - Step-by-step testing instructions
  - Expected outcomes per scenario
  - Troubleshooting common issues
  - Link to automated test suites

### Final Polishing
- [ ] **T073** Accessibility compliance review
  - Run axe DevTools on all pages
  - Fix all critical/serious violations
  - Test with screen reader (VoiceOver/NVDA)
  - Test keyboard-only navigation
  - Verify WCAG 2.1 AA compliance
  - Add skip links for main content

- [ ] **T074** Error handling improvements
  - Add user-friendly error messages
  - Add retry logic for failed API calls
  - Add fallback UI for broken components
  - Add network offline detection
  - Add error logging to activity log

- [ ] **T075** Production readiness checklist
  - Environment variables documented
  - Database migrations tested (up/down)
  - CORS configured correctly
  - Rate limiting enabled
  - Security headers configured
  - Logging configured (backend & frontend)
  - Health check endpoints working
  - Docker Compose production config
  - Backup and restore procedures documented

---

## Dependencies Summary

### Sequential Dependencies
```
Backend Foundation (T001-T004)
  → Schemas (T005-T007) [All parallel]
  → Contract Tests (T008-T018) [All parallel, must fail first]
  → CRUD (T019-T021) [All parallel]
  → Routes (T022-T024)
  → Activity Logging (T025-T026)

CSS Design System (T027-T032) [Mostly parallel]
  → Dashboard Widgets (T033-T038) [All parallel]
  → Dashboard Layout (T039-T040)

Preferences Backend (T019, T022)
  → Preferences Frontend (T041-T045)

Notifications Backend (T020, T023)
  → Notifications Frontend (T046-T050)

Mobile Optimization (T051-T056) [Can start after CSS foundation]

Integration Tests (T057-T064) [All parallel, after features complete]

Performance (T065-T068) [All parallel, final phase]

Documentation (T069-T075) [Mostly parallel, continuous]
```

### Critical Path
```
T001 (UserPreferences model) → T004 (Migration) → T005 (Schemas) →
T008-T012 (Contract tests) → T019 (Preferences CRUD) → T022 (Preferences routes) →
T027 (Design tokens) → T028-T032 (CSS foundation) → T033-T038 (Widgets) →
T039 (Enhanced Dashboard) → T041-T045 (Preferences integration) →
T065-T068 (Performance validation) → T075 (Production readiness)
```

## Parallel Execution Examples

### Example 1: Database Models (T001-T003)
```bash
# All three models can be created in parallel (different files)
# T001, T002, T003 simultaneously
```

### Example 2: Contract Tests (T008-T018)
```bash
# All 11 contract tests in parallel
pytest backend/tests/contract/test_preferences_*.py backend/tests/contract/test_notifications_*.py -n auto
```

### Example 3: CSS Foundation (T027-T032)
```bash
# All CSS files in parallel (different files)
# T027-T032 simultaneously
```

### Example 4: Dashboard Widgets (T033-T038)
```bash
# All widget components in parallel (different files)
# T033-T038 simultaneously
```

## Notes
- **[P] tasks** = different files, no dependencies → safe for parallel execution
- **TDD Required**: Contract tests (T008-T018) MUST be written and MUST FAIL before implementing routes
- **CSS First**: Design system (T027-T032) must be complete before building styled components
- **Backend Before Frontend**: Preferences/Notifications backend (T019-T026) must be done before frontend integration
- **Commit frequently**: After each logical task or group of related tasks
- **Code quality**: Run Black/isort (backend), ESLint/Prettier (frontend) before commits
- **Test coverage**: Aim for ≥80% on new code

## Task Completion Checklist

After completing all tasks, verify:
- [ ] All contract tests pass (11 new tests for preferences/notifications)
- [ ] All integration tests pass (8 validation scenarios)
- [ ] CSS design system fully implemented and documented
- [ ] Dark mode works correctly
- [ ] Dashboard 2-column layout responsive on all devices
- [ ] User preferences persist across sessions (LocalStorage + backend)
- [ ] Notifications system fully functional with real-time updates
- [ ] Activity feed shows recent actions
- [ ] Mobile experience optimized (touch targets, swipe gestures, responsive)
- [ ] Accessibility compliance (WCAG 2.1 AA, keyboard nav, screen reader)
- [ ] Performance benchmarks met (page load <3s, API <500ms, 100+ concurrent users)
- [ ] Code coverage ≥80% on new code
- [ ] All constitutional checks pass (TDD, type safety, modularity)
- [ ] Documentation complete (API docs, user guide, README)
- [ ] Production readiness checklist complete

---

*Tasks generated: 2025-10-05*
*Total tasks: 75 (Backend: 26, CSS/Design: 20, Frontend Features: 15, Mobile: 6, Testing: 8)*
*Estimated parallel task groups: 12-15 (significant time savings)*
*Ready for implementation following TDD principles*
*Focus: Visual polish, UX enhancements, new features on 95% complete backend*
