# Quickstart Guide: BWARM Dashboard Improvements

**Feature**: Dashboard UI/UX Enhancements
**Branch**: `001-bwarm-dashboard-high`
**Date**: 2025-10-05

## Overview

This quickstart validates the implementation of dashboard improvements including visual design system, enhanced layout, user preferences, notifications, and mobile optimization.

## Prerequisites

- Backend running: `uvicorn main:app --reload` (port 8000)
- Frontend running: `npm run dev` (port 5173)
- PostgreSQL database with migrations applied
- Test user account: `publisher@example.com` / password

## Test Scenarios

### Scenario 1: Visual Design System

**Goal**: Verify CSS design system is implemented and dark mode works

**Steps**:
1. Navigate to http://localhost:5173
2. Login with test credentials
3. Observe dashboard styling:
   - Color palette matches design tokens
   - Typography uses Inter font family
   - Spacing follows 8px grid
   - Shadows and borders render correctly
4. Click theme toggle in header
5. Verify dark mode applies:
   - Background changes to dark gray (#1F2937)
   - Text changes to light (#F9FAFB)
   - All components adapt properly

**Expected Results**:
- ✅ Professional visual design with consistent colors
- ✅ Smooth theme toggle animation (300ms transition)
- ✅ No visual glitches or layout shifts
- ✅ All text remains readable in both modes (4.5:1 contrast ratio)

**Validation**:
```bash
# Check CSS custom properties are defined
curl http://localhost:5173 | grep "var(--color-primary"
# Should return CSS with custom properties

# Lighthouse accessibility score
npx lighthouse http://localhost:5173/login --only-categories=accessibility
# Target: Score ≥ 90
```

---

### Scenario 2: Enhanced Dashboard Layout

**Goal**: Verify 2-column responsive grid layout with new widgets

**Steps**:
1. Navigate to dashboard (/)
2. Observe layout structure:
   - Left column (70%): Stats grid, dual chart panel, recent uploads
   - Right sidebar (30%, sticky): Activity feed, quick actions, insights
3. Resize browser to tablet width (768px)
   - Sidebar should stack below main content
4. Resize to mobile width (375px)
   - Single column layout
   - Horizontal scrollable stats cards
   - Bottom sheet for quick actions

**Expected Results**:
- ✅ 2-column grid on desktop (≥1024px)
- ✅ Stacked layout on tablet (768-1023px)
- ✅ Mobile-first layout on phone (<768px)
- ✅ All content accessible at all breakpoints
- ✅ No horizontal scrolling on mobile

**Validation**:
```typescript
// Component test
describe('Dashboard Layout', () => {
  it('renders 2-column grid on desktop', () => {
    render(<Dashboard />, { viewport: { width: 1280 } });
    expect(screen.getByTestId('dashboard-layout'))
      .toHaveStyle('grid-template-columns: 1fr 380px');
  });

  it('stacks layout on mobile', () => {
    render(<Dashboard />, { viewport: { width: 375 } });
    expect(screen.getByTestId('dashboard-layout'))
      .toHaveStyle('grid-template-columns: 1fr');
  });
});
```

---

### Scenario 3: Enhanced Stat Cards with Trends

**Goal**: Verify stat cards show trends, sparklines, and drill-down

**Steps**:
1. Observe stat cards in dashboard grid
2. Verify each card shows:
   - Primary metric value (e.g., "125,847 Total Works")
   - Trend indicator (e.g., "+12% ↑" in green)
   - Sparkline chart (7-day trend)
   - Comparison text (e.g., "+15K this month")
   - "View Details →" button
3. Click "View Details" on "Works with ISWC" card
4. Verify navigation to /works with ISWC filter applied

**Expected Results**:
- ✅ 4 enhanced stat cards displayed
- ✅ Trend indicators color-coded (green up, red down, gray neutral)
- ✅ Sparklines render smoothly (animated on load)
- ✅ Drill-down navigates to filtered views
- ✅ Cards responsive (stack on mobile)

**API Contract Test**:
```python
def test_statistics_includes_trends(client, auth_headers):
    response = client.get('/api/v1/works/statistics', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Verify trend data present
    assert 'total_works' in data
    assert 'total_works_trend' in data  # NEW: trend percentage
    assert 'monthly_trend' in data
    assert len(data['monthly_trend']) >= 7  # At least 7 days
```

---

### Scenario 4: User Preferences Persistence

**Goal**: Verify user preferences save and load correctly

**Steps**:
1. Navigate to dashboard
2. Toggle dark mode ON
3. Rearrange dashboard widgets (if drag-drop enabled)
4. Change items per page to 25 (in settings)
5. Refresh browser (F5)
6. Verify preferences persisted:
   - Dark mode still active
   - Widget layout retained
   - Items per page setting saved

**Expected Results**:
- ✅ Preferences save to LocalStorage immediately
- ✅ Preferences sync to backend API within 5 seconds
- ✅ Preferences load on page refresh (<500ms)
- ✅ Cross-device sync (login on different browser shows same prefs)

**API Contract Test**:
```python
def test_preferences_crud(client, auth_headers):
    # Create/Update preferences
    payload = {
        'theme': 'dark',
        'items_per_page': 25,
        'dashboard_layout': {
            'widgets': [{'id': 'stats', 'position': {'x': 0, 'y': 0}}]
        }
    }
    response = client.put('/api/v1/preferences', json=payload, headers=auth_headers)
    assert response.status_code == 200

    # Read preferences
    response = client.get('/api/v1/preferences', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['theme'] == 'dark'
    assert data['items_per_page'] == 25
```

---

### Scenario 5: Real-Time Activity Feed

**Goal**: Verify activity feed shows live updates

**Steps**:
1. Open dashboard in browser A
2. Open second browser B with same user
3. In browser B: Upload a catalog file
4. In browser A: Observe activity feed (30s max delay)
5. Verify new activity appears:
   - Icon: Upload icon
   - Text: "Catalog uploaded: filename.csv"
   - Timestamp: "2 min ago"
   - Action: "View" button links to results

**Expected Results**:
- ✅ Activity feed polls every 30 seconds (or WebSocket if implemented)
- ✅ New activities appear without page refresh
- ✅ Activities sorted by timestamp (newest first)
- ✅ "View" action navigates correctly
- ✅ Activity types color-coded (success=green, error=red, info=blue)

**Integration Test**:
```python
def test_activity_feed_updates(client, auth_headers):
    # Upload catalog (creates activity)
    files = {'file': ('test.csv', 'track,artist\nTest,Artist', 'text/csv')}
    client.post('/api/v1/catalog/upload', files=files, headers=auth_headers)

    # Fetch activity feed
    response = client.get('/api/v1/activity', headers=auth_headers)
    assert response.status_code == 200
    activities = response.json()['data']

    # Verify upload activity exists
    assert len(activities) > 0
    assert activities[0]['action'] == 'catalog.upload'
    assert 'test.csv' in activities[0]['description']
```

---

### Scenario 6: Notification System

**Goal**: Verify notifications are created and displayed

**Steps**:
1. Upload a small catalog (100 tracks)
2. Wait for processing to complete (~10 seconds)
3. Verify notification appears:
   - Bell icon in header shows badge (count: 1)
   - Click bell to open notifications dropdown
   - Notification shows: "Upload Complete - 100 tracks processed"
   - Click notification to navigate to results
4. Mark notification as read
5. Verify badge count decreases to 0

**Expected Results**:
- ✅ Notification created on upload complete
- ✅ Badge shows unread count
- ✅ Notification dropdown renders correctly
- ✅ Click navigates to related entity
- ✅ Mark as read updates UI immediately
- ✅ Bulk "Mark all as read" works

**API Contract Test**:
```python
def test_notifications_workflow(client, auth_headers, upload_fixture):
    # Simulate upload complete (creates notification)
    upload_id = upload_fixture['id']
    # (Background task would create notification)

    # Get unread count
    response = client.get('/api/v1/notifications/unread-count', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['count'] > 0

    # List notifications
    response = client.get('/api/v1/notifications', headers=auth_headers)
    assert response.status_code == 200
    notifications = response.json()['data']
    assert len(notifications) > 0

    notif_id = notifications[0]['id']

    # Mark as read
    response = client.put(f'/api/v1/notifications/{notif_id}/read', headers=auth_headers)
    assert response.status_code == 200

    # Verify unread count decreased
    response = client.get('/api/v1/notifications/unread-count', headers=auth_headers)
    assert response.json()['count'] == 0
```

---

### Scenario 7: Mobile Experience

**Goal**: Verify dashboard works on mobile devices

**Steps**:
1. Open Chrome DevTools
2. Enable device toolbar (Cmd+Shift+M)
3. Select "iPhone 14 Pro" (390x844)
4. Navigate to dashboard
5. Verify mobile optimizations:
   - Touch targets ≥ 44x44px
   - No horizontal scrolling
   - Bottom sheet modals (not centered)
   - Swipeable upload cards
   - Readable text (≥16px base size)
6. Test gestures:
   - Tap stat card to drill down
   - Swipe upload card to delete
   - Pull to refresh (if implemented)

**Expected Results**:
- ✅ All interactions work with touch
- ✅ No hover-dependent features
- ✅ Bottom navigation or bottom sheets for actions
- ✅ Performance: Lighthouse mobile score ≥ 85
- ✅ No layout shifts or jank

**Mobile Performance Test**:
```bash
# Lighthouse mobile audit
npx lighthouse http://localhost:5173 \
  --preset=desktop \
  --emulated-form-factor=mobile \
  --throttling.cpuSlowdownMultiplier=4 \
  --only-categories=performance,accessibility

# Target scores:
# Performance: ≥ 85
# Accessibility: ≥ 90
# First Contentful Paint: < 2.5s
# Largest Contentful Paint: < 4.0s
# Cumulative Layout Shift: < 0.25
```

---

### Scenario 8: Accessibility Compliance

**Goal**: Verify WCAG 2.1 AA compliance

**Steps**:
1. Navigate to dashboard
2. Enable screen reader (VoiceOver on Mac, NVDA on Windows)
3. Tab through all interactive elements:
   - Stat cards, chart controls, activity feed items, notifications
4. Verify announcements:
   - Button labels clear ("View details for Works with ISWC")
   - Form inputs have labels
   - Error messages read aloud
5. Test keyboard navigation:
   - Tab/Shift+Tab to navigate
   - Enter/Space to activate
   - Escape to close modals
6. Run axe DevTools audit

**Expected Results**:
- ✅ All interactive elements keyboard accessible
- ✅ Focus visible (outline or highlight)
- ✅ ARIA labels on icon-only buttons
- ✅ Semantic HTML (header, nav, main, aside)
- ✅ Color contrast ≥ 4.5:1 for text
- ✅ No critical or serious axe violations

**Accessibility Test**:
```typescript
describe('Dashboard Accessibility', () => {
  it('has no axe violations', async () => {
    const { container } = render(<Dashboard />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('supports keyboard navigation', () => {
    render(<Dashboard />);

    // Tab to first interactive element
    userEvent.tab();
    expect(screen.getByRole('button', { name: /theme toggle/i }))
      .toHaveFocus();

    // Tab to stat card drill-down
    userEvent.tab();
    expect(screen.getByRole('button', { name: /view details/i }))
      .toHaveFocus();
  });
});
```

---

## Performance Benchmarks

### Dashboard Load Performance

**Test**: Load dashboard page and measure performance

```bash
# Backend response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/works/statistics

# Target: < 200ms server response
# Target: < 500ms total (including network)
```

**Frontend Bundle Size**:
```bash
npm run build
ls -lh dist/assets/*.js

# Target: Main bundle < 250KB gzipped
# Target: Vendor bundle < 150KB gzipped
# Target: Total initial load < 500KB
```

### Concurrent User Load Test

**Tool**: k6 load testing

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],  // 95% < 3s
    http_req_failed: ['rate<0.01'],     // Error rate < 1%
  },
};

export default function () {
  const loginRes = http.post('http://localhost:8000/api/v1/auth/login', {
    email: 'publisher@example.com',
    password: 'password',
  });

  const token = loginRes.json('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  // Dashboard stats
  const statsRes = http.get('http://localhost:8000/api/v1/works/statistics', { headers });
  check(statsRes, { 'stats loaded': (r) => r.status === 200 });

  // Activity feed
  const activityRes = http.get('http://localhost:8000/api/v1/activity', { headers });
  check(activityRes, { 'activity loaded': (r) => r.status === 200 });

  sleep(1);
}
```

**Run**:
```bash
k6 run load-test.js

# Expected results:
# ✓ http_req_duration: avg<1s p(95)<3s
# ✓ http_req_failed: rate<1%
# ✓ No database connection errors
# ✓ Redis hit rate > 80%
```

---

## Database Performance Validation

### Index Effectiveness

**Query**: Verify indexes are used for common queries

```sql
-- Unread notifications query
EXPLAIN ANALYZE
SELECT * FROM notifications
WHERE user_id = 'uuid-here'
  AND is_read = false
ORDER BY created_at DESC
LIMIT 10;

-- Expected: Index Scan using notifications_user_id_is_read_created_at_idx
-- Target: Execution time < 5ms

-- User activity history
EXPLAIN ANALYZE
SELECT * FROM activity_logs
WHERE user_id = 'uuid-here'
ORDER BY created_at DESC
LIMIT 50;

-- Expected: Index Scan using activity_logs_user_id_created_at_idx
-- Target: Execution time < 10ms
```

### Query Performance Benchmarks

| Query | Target | Current | Status |
|-------|--------|---------|--------|
| Dashboard statistics | < 100ms | TBD | ⏳ |
| User preferences load | < 50ms | TBD | ⏳ |
| Unread notifications count | < 10ms | TBD | ⏳ |
| Activity feed (50 items) | < 50ms | TBD | ⏳ |
| Works search (full-text) | < 500ms | TBD | ⏳ |

---

## Success Criteria Checklist

### Visual Design System
- [ ] CSS custom properties implemented
- [ ] Dark mode toggle works
- [ ] Color contrast WCAG AA compliant
- [ ] Typography scales correctly
- [ ] Spacing follows 8px grid

### Enhanced Dashboard Layout
- [ ] 2-column grid on desktop
- [ ] Responsive breakpoints work
- [ ] Mobile single-column layout
- [ ] Sticky sidebar functional
- [ ] All widgets render correctly

### User Preferences
- [ ] Preferences save to backend
- [ ] LocalStorage sync works
- [ ] Cross-device sync functional
- [ ] Theme persists on refresh
- [ ] Layout customization saves

### Notifications
- [ ] Notifications created on events
- [ ] Badge shows unread count
- [ ] Dropdown renders correctly
- [ ] Mark as read works
- [ ] Bulk actions functional

### Real-Time Updates
- [ ] Activity feed polls/streams
- [ ] New activities appear live
- [ ] Timestamp updates (relative)
- [ ] Action buttons navigate correctly

### Mobile Experience
- [ ] Touch targets ≥ 44px
- [ ] No horizontal scroll
- [ ] Bottom sheet modals
- [ ] Gestures work (swipe, tap)
- [ ] Performance acceptable

### Accessibility
- [ ] Keyboard navigation complete
- [ ] Screen reader compatible
- [ ] ARIA labels present
- [ ] Focus management correct
- [ ] No critical axe violations

### Performance
- [ ] Dashboard loads < 3s (p95)
- [ ] API responses < 500ms (p90)
- [ ] 100+ concurrent users supported
- [ ] Bundle size < 500KB initial
- [ ] Lighthouse score ≥ 85

---

## Troubleshooting

### Issue: Dark mode not applying
**Solution**: Check localStorage for `user-preferences`, verify theme value, inspect CSS custom properties in DevTools

### Issue: Activity feed not updating
**Solution**: Check TanStack Query refetchInterval, verify API endpoint returns data, check browser console for errors

### Issue: Notifications not appearing
**Solution**: Verify notification creation in database, check unread count API, inspect notification polling logic

### Issue: Mobile layout broken
**Solution**: Check viewport meta tag, verify Tailwind breakpoints, test with real device not just DevTools

### Issue: Slow dashboard load
**Solution**: Check database query execution plans, verify Redis caching, analyze bundle size, use React DevTools Profiler

---

## Completion Checklist

- [ ] All 8 test scenarios pass
- [ ] Performance benchmarks met
- [ ] Accessibility audit clean
- [ ] Mobile testing complete
- [ ] Database indexes verified
- [ ] Load testing successful (100 users)
- [ ] No console errors in browser
- [ ] No server errors in logs
- [ ] Documentation updated
- [ ] Ready for production deployment

---

*Quickstart guide version: 1.0*
*Last updated: 2025-10-05*
*Feature: 001-bwarm-dashboard-high*
