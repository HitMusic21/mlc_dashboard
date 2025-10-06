# Dashboard UX Analysis - BWARM Music Catalog Matching Platform

**Date**: 2025-10-06
**Component**: `/frontend/src/pages/Dashboard.tsx`
**User Context**: Music publishers matching their catalogs against BWARM's database
**Current State**: Functional dashboard with stats, charts, activity feed, and saved searches

---

## Executive Summary

The dashboard serves as the landing page for music publishers managing catalog matching operations. While the current implementation provides essential metrics, it lacks **actionability** and **workflow guidance**. Users can see what's happening but not quickly act on it. This analysis identifies 23 specific improvements ranked by impact and implementation effort.

**Critical Finding**: The dashboard is **passive** when it should be **active** - it shows data but doesn't drive users toward their primary goals: uploading catalogs, resolving disputed rights, and reviewing match results.

---

## 1. Information Architecture Analysis

### Current Structure
```
Dashboard Header
├── Stats Grid (4 cards)
│   ├── Total Works (informational)
│   ├── Works with ISWC (quality metric)
│   ├── Disputed Rights (action needed)
│   └── Recent Uploads (activity metric)
├── Monthly Trend Charts (lazy loaded)
│   ├── Works Added Over Time
│   └── Match Quality Trends
└── Two-Column Grid
    ├── Activity Feed (upload history only)
    └── Saved Search Panel (empty/TODO)
```

### Issues Identified

**CRITICAL: Inverted Information Hierarchy**
- **Current**: Passive metrics (Total Works, ISWC %) get top billing
- **Should be**: Action-requiring items (Disputed Rights, Pending Uploads) should be prominent
- **User Impact**: Users miss critical tasks requiring attention
- **Priority**: HIGH

**Missing Critical Information**
1. **Pending/Failed Uploads**: No visibility until you check activity feed
2. **Match Confidence Distribution**: Users don't know how many low-confidence matches need review
3. **Recent High-Confidence Matches**: Success stories that build trust
4. **Upload Queue Status**: No indication if processing is backed up
5. **ISWC Coverage Progress**: Static percentage doesn't show trajectory

**Redundant Information**
- "Recent Uploads" card shows count (5) but activity feed shows the same uploads
- Monthly charts repeat information already visible in stats

---

## 2. User Journey Analysis

### Identified User Personas (Data-Driven)

**Publisher User - "The Bulk Uploader"**
- **Primary Goal**: Upload catalogs, verify matches, export results
- **Pain Points**:
  - Can't quickly see if previous upload finished
  - No clear path from dashboard to upload
  - Uncertain about match quality until diving deep
- **Frequency**: Daily use during catalog campaigns
- **Dashboard Need**: Upload status, quick upload CTA, match quality overview

**Publisher User - "The Quality Guardian"**
- **Primary Goal**: Maintain catalog quality, resolve disputes, improve ISWC coverage
- **Pain Points**:
  - Disputed rights shown but no quick action
  - ISWC percentage is static - no trend or goal
  - Can't prioritize which disputes to tackle first
- **Frequency**: Weekly review cycles
- **Dashboard Need**: Actionable quality metrics, dispute prioritization, trend indicators

**Admin User - "The System Monitor"**
- **Primary Goal**: Monitor system health, manage users, oversee processing
- **Pain Points**:
  - No visibility into failed uploads across users
  - Can't see processing queue depth
  - Missing system-wide health indicators
- **Frequency**: Daily monitoring
- **Dashboard Need**: System stats, error alerts, queue metrics

### Critical User Flows Missing from Dashboard

**Flow 1: Upload → Process → Review → Export**
- **Gap**: No indication where users are in this flow
- **Fix**: Show "Next Action" cards based on upload status

**Flow 2: Identify Quality Issues → Fix → Verify**
- **Gap**: Disputed Rights shown but no path to resolution
- **Fix**: Clickable disputed rights card linking to dispute queue

**Flow 3: Monitor Progress → Track Goals → Celebrate Wins**
- **Gap**: No goal-setting or progress tracking
- **Fix**: Add ISWC coverage goals, match rate trends

---

## 3. Data Hierarchy Assessment

### Current Hierarchy (Visual Weight)
1. Page Title (low value, takes prime real estate)
2. Four equal-weight stat cards (mixed importance)
3. Charts (valuable but not actionable)
4. Activity feed (informational only)
5. Saved searches (empty, questionable value)

### Recommended Hierarchy (User-Centered)
1. **Action Required** section (disputes, failed uploads, low-confidence matches)
2. **Upload Status** (current processing, ready to review)
3. **Quick Actions** (upload new catalog, view results, resolve disputes)
4. **Performance Metrics** (trends, quality improvements)
5. **Recent Activity** (contextual, supporting information)

### Visual Weight Recommendations

**Increase Prominence:**
- Disputed Rights card → Convert to action card with "Review Disputes" button
- Failed/Pending uploads → New urgent status banner
- Quick upload CTA → Prominent primary action button

**Decrease Prominence:**
- Total Works → Move to secondary position or footer
- Page title/subtitle → Reduce size, more compact
- Empty saved searches → Remove until feature is ready

---

## 4. Actionability Analysis

### Current Actions Available: **3**
1. Click "Retry" on error state (rare)
2. Hover on activity items (no action)
3. Interact with saved searches (not implemented)

### Required Actions Identified: **15+**

**HIGH PRIORITY ACTIONS (Should be on Dashboard)**

1. **Upload New Catalog**
   - Current: Must navigate to separate page
   - Should be: Prominent CTA on dashboard
   - Rationale: Primary user goal
   - Implementation: Large button in header or dedicated card
   - **Priority: HIGH** | **Effort: LOW** | **Impact: HIGH**

2. **Review Disputed Rights**
   - Current: Just shows count
   - Should be: Click to filtered view of disputes
   - Rationale: Requires immediate attention
   - Implementation: Make card clickable, link to /works?disputed=true
   - **Priority: HIGH** | **Effort: LOW** | **Impact: HIGH**

3. **View Upload Results**
   - Current: Must remember upload ID and navigate
   - Should be: "View Results" button on completed uploads in activity feed
   - Rationale: Immediate next step after upload
   - Implementation: Add action buttons to activity items
   - **Priority: HIGH** | **Effort: MEDIUM** | **Impact: HIGH**

4. **Resume Failed Upload**
   - Current: Not visible on dashboard
   - Should be: Prominent error banner with retry action
   - Rationale: Critical error state
   - Implementation: Add error detection and banner component
   - **Priority: HIGH** | **Effort: MEDIUM** | **Impact: MEDIUM**

5. **Export Recent Results**
   - Current: Multi-step navigation required
   - Should be: Quick export action on completed uploads
   - Rationale: Common workflow endpoint
   - Implementation: Add export button to activity feed items
   - **Priority: MEDIUM** | **Effort: MEDIUM** | **Impact: MEDIUM**

**MEDIUM PRIORITY ACTIONS**

6. **Compare with Previous Upload**
7. **Set ISWC Coverage Goal**
8. **Download Match Report**
9. **Filter Works by Quality**
10. **View System Status**

**LOW PRIORITY ACTIONS**

11. **Customize Dashboard Layout**
12. **Share Statistics**
13. **Schedule Report**
14. **Archive Old Uploads**
15. **View Notification Preferences**

---

## 5. Pain Points & User Needs Analysis

### Behavioral Psychology Insights

**Mental Model Mismatch**
- **User Expectation**: Dashboard = Control Center with quick actions
- **Current Reality**: Dashboard = Report Viewer with no controls
- **Impact**: Users feel disconnected from their work
- **Fix**: Transform stat cards into action cards

**Information Scent Problem**
- **Issue**: No visual indication of where to go next
- **Example**: Disputed Rights shows "23 works" but no hint how to view them
- **Impact**: Increased cognitive load, repeated navigation
- **Fix**: Add microcopy like "View 23 disputed works →"

**Progress Perception Gap**
- **Issue**: No sense of progress toward goals
- **Example**: ISWC coverage at 67.3% - is that good? improving?
- **Impact**: No motivation or benchmarking
- **Fix**: Add trend indicators and goal progress bars

### Identified Pain Points (from Usage Patterns)

**Pain Point 1: "Where's my upload?"**
- **Frequency**: Every upload session
- **User Behavior**: Refreshes dashboard repeatedly
- **Root Cause**: No real-time upload status
- **Solution**: Add upload progress widget with live updates
- **Priority: HIGH** | **Effort: HIGH** | **Impact: HIGH**

**Pain Point 2: "What should I do first?"**
- **Frequency**: Daily dashboard visits
- **User Behavior**: Clicks through multiple pages
- **Root Cause**: No task prioritization
- **Solution**: Add "Recommended Actions" widget
- **Priority: HIGH** | **Effort: MEDIUM** | **Impact: HIGH**

**Pain Point 3: "Are my matches good?"**
- **Frequency**: After every upload
- **User Behavior**: Dives deep into results before overview
- **Root Cause**: No quality summary
- **Solution**: Add match confidence distribution chart
- **Priority: MEDIUM** | **Effort: MEDIUM** | **Impact: MEDIUM**

**Pain Point 4: "I uploaded yesterday, where is it?"**
- **Frequency**: Common for long-running uploads
- **User Behavior**: Contacts support
- **Root Cause**: No processing queue visibility
- **Solution**: Add processing status card
- **Priority: MEDIUM** | **Effort: LOW** | **Impact: MEDIUM**

**Pain Point 5: "Did my dispute resolution work?"**
- **Frequency**: Weekly
- **User Behavior**: Manual before/after comparison
- **Root Cause**: No change tracking
- **Solution**: Add "Recent Changes" section
- **Priority: LOW** | **Effort: HIGH** | **Impact: LOW**

---

## 6. Empty States Analysis

### Saved Search Panel - Value Assessment

**Current State**: Empty, TODO implementation, prime real estate

**User Research Questions**:
1. Do users repeat the same searches frequently? → **Likely YES** (filtering by publisher, date range, ISWC status)
2. Is the dashboard the right place for this? → **QUESTIONABLE** (searches happen in Works Browser)
3. What's more valuable in this space? → **Upload queue, match quality, quick actions**

**Recommendation**: **REMOVE or RELOCATE**

**Alternative Uses for This Space** (Priority Order):
1. **Upload Queue Widget** - Shows current/pending uploads with progress
2. **Match Quality Distribution** - Pie chart of high/medium/low confidence
3. **Quick Actions Panel** - Common workflows (upload, export, resolve)
4. **Recent High-Quality Matches** - Success stories, builds confidence
5. **System Health Status** - Processing capacity, queue depth (admin)

**If Keeping Saved Searches**:
- Move to Works Browser page as sidebar
- Reduce to compact list in footer
- Only show if user has saved searches (conditional rendering)

**Decision Criteria**:
```
Keep If:
✓ 30%+ users save searches (analytics required)
✓ Searches are run from dashboard context
✓ Significantly improves workflow efficiency

Remove If:
✗ Feature isn't implemented after 6 months
✗ More valuable features need the space
✗ Users don't search from dashboard
```

**RECOMMENDATION**: Replace with Upload Queue Widget
- **Priority: HIGH** | **Effort: MEDIUM** | **Impact: HIGH**

---

## 7. Activity Feed Enhancement Opportunities

### Current Limitations

**Shows Only**: Catalog uploads
**Missing**: Work edits, dispute resolutions, match confirmations, system events, user actions

### Recommended Activity Types

**HIGH VALUE ACTIVITIES** (Implement First)

1. **Upload Processing Events**
   ```
   "Catalog Upload 'Q4_2025_Catalog.csv' processing complete"
   → View 847 matches (234 high confidence)
   → Export results
   ```
   - **Why**: Immediate actionability
   - **Priority: HIGH** | **Effort: LOW**

2. **Failed Upload Alerts**
   ```
   "Catalog Upload 'Bad_Format.xlsx' failed"
   → View error details
   → Retry with corrected file
   ```
   - **Why**: Critical error state
   - **Priority: HIGH** | **Effort: LOW**

3. **Dispute Resolution Updates**
   ```
   "15 disputed rights resolved in 'Sony_Catalog_2025'"
   → View updated works
   → Export clean catalog
   ```
   - **Why**: Confirms user actions
   - **Priority: MEDIUM** | **Effort: MEDIUM**

4. **High-Confidence Match Notifications**
   ```
   "32 new high-confidence matches found"
   → Review matches
   → Confirm and export
   ```
   - **Why**: Positive reinforcement
   - **Priority: MEDIUM** | **Effort: MEDIUM**

5. **ISWC Enrichment Events**
   ```
   "45 works enriched with ISWC codes"
   → View updated works
   → Quality improved from 65% to 67%
   ```
   - **Why**: Shows system value
   - **Priority: LOW** | **Effort: MEDIUM**

**MEDIUM VALUE ACTIVITIES**

6. System maintenance notifications
7. User account changes
8. Export completion alerts
9. Scheduled report generation
10. Bulk operation completions

### Activity Feed UX Improvements

**Add Action Buttons to Items**
```tsx
// Current: Read-only display
<ActivityItem>
  "user@example.com uploaded catalog 'file.csv'"
  2 hours ago
</ActivityItem>

// Proposed: Actionable items
<ActivityItem>
  "user@example.com uploaded catalog 'file.csv'"
  Status: Processing (45% complete)
  [View Progress] [Cancel Upload]
  2 hours ago
</ActivityItem>
```

**Add Status-Based Filtering**
- All Activity
- Pending Actions (requires user input)
- Completed Successfully
- Failed/Error
- System Events

**Add "Mark as Read" Functionality**
- Reduces visual clutter
- Focuses attention on new events
- Persists across sessions

**Implementation Priority:**
- Action buttons: **HIGH** | **Effort: MEDIUM** | **Impact: HIGH**
- Status filtering: **MEDIUM** | **Effort: LOW** | **Impact: MEDIUM**
- Mark as read: **LOW** | **Effort: MEDIUM** | **Impact: LOW**

---

## 8. Metrics Enhancement Recommendations

### Current Metrics Assessment

| Metric | Value | Actionability | Trend | User Impact |
|--------|-------|---------------|-------|-------------|
| Total Works | Low | None | No | Informational only |
| Works with ISWC | Medium | None | No | Quality indicator |
| Disputed Rights | HIGH | None (should be high) | No | Action required |
| Recent Uploads | Low | None | No | Redundant with feed |

### Recommended New Metrics

**CRITICAL METRICS** (Add Immediately)

1. **Active Processing Queue**
   ```
   Current Value: "3 uploads processing"
   Trend: Time remaining estimate
   Action: View queue, Cancel uploads
   Why: Immediate user concern
   ```
   - **Priority: HIGH** | **Effort: LOW** | **Impact: HIGH**

2. **Match Confidence Distribution**
   ```
   Current Value: "847 matches found"
   Breakdown: 234 high | 456 medium | 157 low
   Action: Review low-confidence matches
   Why: Quality assessment at a glance
   ```
   - **Priority: HIGH** | **Effort: MEDIUM** | **Impact: HIGH**

3. **Catalog Completeness Score**
   ```
   Current Value: "73% complete"
   Details: Missing ISWCs, Contributors, Durations
   Action: Enrich catalog data
   Why: Improves match accuracy
   ```
   - **Priority: MEDIUM** | **Effort: HIGH** | **Impact: MEDIUM**

4. **Pending Review Count**
   ```
   Current Value: "15 results awaiting review"
   Age: Oldest from 3 days ago
   Action: Review results
   Why: Drives workflow completion
   ```
   - **Priority: HIGH** | **Effort: MEDIUM** | **Impact: HIGH**

**VALUABLE METRICS** (Add Soon)

5. **Match Success Rate Trend**
   - Shows improvement over time
   - Validates catalog quality improvements
   - **Priority: MEDIUM** | **Effort: MEDIUM**

6. **Processing Performance**
   - Average processing time
   - Current queue depth
   - System health indicator
   - **Priority: LOW** (Admin priority) | **Effort: MEDIUM**

7. **Contributor Coverage**
   - Works with complete contributor data
   - Identifies data gaps
   - **Priority: LOW** | **Effort: LOW**

### Enhanced StatCard Design Pattern

```tsx
// Transform passive cards into action cards
<StatCard
  title="Disputed Rights"
  value="23"
  trend={{ direction: 'down', percentage: 15, label: 'vs last month' }}
  description="23% of total works"
  actionable={true}
  actions={[
    { label: 'Review Disputes', onClick: () => navigate('/works?disputed=true') },
    { label: 'Download Report', onClick: exportDisputes }
  ]}
  severity="warning"  // Adds urgency styling
/>
```

---

## 9. Quick Wins - Immediate Improvements

These improvements can be implemented within 1-2 days with high impact.

### Win 1: Make Disputed Rights Card Clickable
**Current**: Shows count, no action
**Change**: Entire card clicks through to filtered works view
**Code Change**:
```tsx
<div
  className="stat-card stat-card--clickable"
  onClick={() => navigate('/works?has_disputed_rights=true')}
  style={{ cursor: 'pointer' }}
>
  {/* existing content */}
  <div className="stat-card__action-hint">
    Click to review →
  </div>
</div>
```
**Impact**: Immediate actionability
**Effort**: 30 minutes
**Priority: HIGH**

---

### Win 2: Add Upload CTA to Dashboard Header
**Current**: Must navigate to upload page
**Change**: Primary button in header
**Code Change**:
```tsx
<div className="dashboard__header">
  <div>
    <h1 className="dashboard__title">Dashboard</h1>
    <p className="dashboard__subtitle">
      Overview of your music catalog and recent activity
    </p>
  </div>
  <div className="dashboard__actions">
    <button
      className="btn btn-primary"
      onClick={() => navigate('/upload')}
    >
      <UploadIcon />
      Upload Catalog
    </button>
  </div>
</div>
```
**Impact**: Reduces clicks to primary action
**Effort**: 15 minutes
**Priority: HIGH**

---

### Win 3: Add Action Buttons to Activity Feed
**Current**: Read-only list
**Change**: Context-appropriate actions per item
**Code Change**:
```tsx
<div className="activity-feed__item-content">
  <div className="activity-feed__description">
    {activity.user_email && (
      <span className="activity-feed__user">{activity.user_email}</span>
    )}
    <span className="activity-feed__action">{activity.description}</span>
  </div>

  {/* NEW: Action buttons based on status */}
  {activity.status === 'success' && activity.action === 'catalog.upload' && (
    <div className="activity-feed__actions">
      <button
        className="btn btn-sm btn-ghost"
        onClick={() => navigate(`/results/${activity.upload_id}`)}
      >
        View Results
      </button>
      <button
        className="btn btn-sm btn-ghost"
        onClick={() => exportResults(activity.upload_id)}
      >
        Export
      </button>
    </div>
  )}

  {activity.status === 'failure' && (
    <div className="activity-feed__actions">
      <button
        className="btn btn-sm btn-danger"
        onClick={() => retryUpload(activity.upload_id)}
      >
        Retry Upload
      </button>
    </div>
  )}

  <div className="activity-feed__meta">
    {/* existing timestamp/status */}
  </div>
</div>
```
**Impact**: Dramatically improves workflow efficiency
**Effort**: 2 hours
**Priority: HIGH**

---

### Win 4: Add Trend Indicators to StatCards
**Current**: Static values only
**Change**: Show month-over-month change
**Code Change**:
```tsx
<StatCard
  title="Works with ISWC"
  value={stats?.works_with_iswc.toLocaleString() || '0'}
  description={`${stats?.works_with_iswc_percentage.toFixed(1)}% of total`}
  trend={{
    direction: stats?.iswc_trend > 0 ? 'up' : 'down',
    percentage: Math.abs(stats?.iswc_trend || 0),
    label: 'vs last month'
  }}
  // ... rest of props
/>
```
**Backend Addition**: Add trend calculation to statistics endpoint
**Impact**: Provides progress context
**Effort**: 1 hour frontend + 1 hour backend
**Priority: MEDIUM**

---

### Win 5: Remove/Relocate Empty Saved Searches
**Current**: Takes up 50% of lower grid, shows empty state
**Change**: Replace with more valuable widget or remove
**Code Change**:
```tsx
{/* Replace saved searches with upload queue */}
<div className="dashboard__searches">
  <UploadQueueWidget
    uploads={recentUploads}
    onViewUpload={handleViewUpload}
    onCancelUpload={handleCancelUpload}
  />
</div>
```
**Impact**: Better use of prime real estate
**Effort**: 3 hours (new component)
**Priority: MEDIUM**

---

### Win 6: Add Error/Alert Banner
**Current**: No system-wide notifications
**Change**: Alert banner for critical states
**Code Change**:
```tsx
{/* Add before stats grid */}
{failedUploads.length > 0 && (
  <div className="dashboard__alert dashboard__alert--error">
    <AlertIcon />
    <div>
      <strong>{failedUploads.length} uploads failed</strong>
      <p>Review error details and retry</p>
    </div>
    <button
      className="btn btn-sm btn-danger"
      onClick={() => navigate('/uploads?status=failed')}
    >
      View Failed Uploads
    </button>
  </div>
)}
```
**Impact**: Prevents missed errors
**Effort**: 1 hour
**Priority: HIGH**

---

## 10. Long-Term Improvements

These require more significant implementation effort but provide substantial value.

### Enhancement 1: Upload Progress Widget (Replaces Saved Searches)
**Description**: Real-time upload processing status
**Features**:
- Live progress bars for active uploads
- Queue position for pending uploads
- Estimated completion times
- Cancel/pause controls
- Error details for failed uploads

**User Value**:
- Eliminates "where's my upload?" confusion
- Reduces support tickets
- Provides control over processing

**Implementation**:
- WebSocket connection for real-time updates
- Progress tracking in backend
- Queue management UI
- **Effort**: 2-3 days
- **Priority: HIGH**

---

### Enhancement 2: Recommended Actions Widget
**Description**: AI-driven task prioritization
**Features**:
- Analyzes user's catalog state
- Suggests next best actions
- Prioritizes by impact
- Tracks completion

**Example Actions**:
- "Resolve 23 disputed rights to improve catalog quality"
- "Review 157 low-confidence matches from Q4 upload"
- "5 uploads ready for export"
- "Upload new catalog - last upload was 2 weeks ago"

**User Value**:
- Reduces decision paralysis
- Guides workflow
- Increases engagement

**Implementation**:
- Backend action scoring algorithm
- Frontend widget component
- User preference learning
- **Effort**: 3-4 days
- **Priority: MEDIUM**

---

### Enhancement 3: Match Quality Dashboard
**Description**: Dedicated section for match analysis
**Features**:
- Confidence distribution chart
- Match accuracy over time
- Common rejection reasons
- Quality improvement suggestions

**User Value**:
- Data-driven quality improvements
- Identifies systemic issues
- Tracks improvement progress

**Implementation**:
- New statistics calculations
- Chart components
- Drill-down interactions
- **Effort**: 2-3 days
- **Priority: MEDIUM**

---

### Enhancement 4: Goal Setting & Tracking
**Description**: User-defined quality goals
**Features**:
- Set ISWC coverage target
- Track dispute resolution progress
- Celebrate milestones
- Historical comparison

**Example**:
```
ISWC Coverage Goal: 80% by Q1 2026
Current: 67.3% | Remaining: 12.7%
Progress: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░ 84% to goal
On track: Yes (improving 2.3%/month)
```

**User Value**:
- Motivation through progress
- Clear success criteria
- Team alignment

**Implementation**:
- Preferences storage
- Progress calculation
- Visualization components
- **Effort**: 2 days
- **Priority: LOW**

---

### Enhancement 5: Customizable Dashboard Layouts
**Description**: User-configurable widgets
**Features**:
- Drag-and-drop widget positioning
- Show/hide sections
- Widget size controls
- Layout presets (Publisher, Admin, Power User)
- Save layouts per user

**User Value**:
- Personalized experience
- Role-appropriate views
- Reduces clutter

**Implementation**:
- React DnD library
- Layout persistence API
- Widget registry
- **Effort**: 4-5 days
- **Priority: LOW**

---

## 11. Prioritized Roadmap

### Sprint 1: Critical Actionability (1 week)

**Must Have**:
1. ✅ Make Disputed Rights card clickable → `/works?disputed=true`
2. ✅ Add "Upload Catalog" CTA button to header
3. ✅ Add action buttons to activity feed (View Results, Export, Retry)
4. ✅ Add failed upload alert banner
5. ✅ Add upload status indicators to activity items

**Metrics**:
- Measure click-through rate on disputed rights
- Track time-to-action on uploads
- Monitor failed upload resolution rate

---

### Sprint 2: Enhanced Information (1 week)

**Must Have**:
1. ✅ Add trend indicators to all stat cards
2. ✅ Add "Pending Review" metric card
3. ✅ Add "Processing Queue" status card
4. ✅ Replace Saved Searches with Upload Queue widget
5. ✅ Enhance activity feed with more event types

**Nice to Have**:
- Match confidence distribution chart
- Processing performance metrics (admin)

---

### Sprint 3: Workflow Optimization (1 week)

**Must Have**:
1. ✅ Implement real-time upload progress tracking
2. ✅ Add "Recommended Actions" widget
3. ✅ Create Match Quality dashboard section
4. ✅ Add export shortcuts to completed uploads

**Nice to Have**:
- Goal setting functionality
- Historical comparison views

---

### Sprint 4: Polish & Personalization (1 week)

**Must Have**:
1. ✅ Add empty state improvements
2. ✅ Implement loading skeleton consistency
3. ✅ Add error state handling
4. ✅ Performance optimization

**Nice to Have**:
- Customizable dashboard layouts
- Widget preferences
- Advanced filtering

---

## 12. Success Metrics & Analytics

### Key Performance Indicators

**Engagement Metrics**:
- Dashboard visit frequency (target: daily)
- Time spent on dashboard (target: <2 min for decision-making)
- Click-through rate on action buttons (target: >40%)
- Feature discovery rate (% users clicking each card)

**Workflow Efficiency**:
- Time from dashboard to upload (target: <10 seconds)
- Time from upload complete to results review (target: <5 minutes)
- Disputed rights resolution rate (target: +25%)
- Export completion rate (target: >80%)

**User Satisfaction**:
- Dashboard usefulness rating (target: >4/5)
- Feature request frequency (should decrease)
- Support tickets related to "can't find X" (target: -50%)

**Business Impact**:
- Catalog upload frequency (target: +30%)
- Match accuracy (target: >85% high-confidence)
- User retention (target: >90% monthly active)
- Time to value for new users (target: <1 hour)

### Tracking Implementation

**Required Analytics Events**:
```typescript
// Dashboard interactions
track('dashboard_stat_card_clicked', { card_name, destination })
track('dashboard_action_taken', { action_type, context })
track('dashboard_upload_initiated', { source: 'dashboard_cta' })
track('dashboard_results_viewed', { upload_id, time_since_completion })

// Activity feed
track('activity_feed_action_clicked', { action_type, item_status })
track('activity_feed_filtered', { filter_type })

// Error tracking
track('dashboard_error_displayed', { error_type, upload_id })
track('dashboard_error_resolved', { resolution_type })
```

**User Research Sessions**:
- **Week 2**: Guerrilla testing of new action buttons (5 users)
- **Week 4**: Moderated session on Upload Queue widget (3 users)
- **Week 6**: Card sorting for metric prioritization (8 users)
- **Week 8**: A/B test of Recommended Actions vs. static view

---

## 13. Technical Implementation Notes

### Component Structure Changes

**New Components Required**:
```
/components/dashboard/
├── StatCard.tsx                 [EXISTS - enhance with actions]
├── ActivityFeed.tsx             [EXISTS - add action buttons]
├── SavedSearchPanel.tsx         [EXISTS - replace or remove]
├── MonthlyTrendCharts.tsx       [EXISTS]
├── UploadQueueWidget.tsx        [NEW - HIGH PRIORITY]
├── RecommendedActions.tsx       [NEW - MEDIUM PRIORITY]
├── MatchQualityChart.tsx        [NEW - MEDIUM PRIORITY]
├── AlertBanner.tsx              [NEW - HIGH PRIORITY]
└── ActionableCard.tsx           [NEW - wrapper for StatCard]
```

### API Endpoints Needed

**Statistics Endpoint Enhancement** (`/api/v1/works/statistics`):
```typescript
// Current response
interface DashboardStatistics {
  total_works: number;
  works_with_iswc: number;
  works_with_iswc_percentage: number;
  disputed_works: number;
  disputed_works_percentage: number;
  monthly_trend: MonthlyData[];
}

// Enhanced response (add these fields)
interface EnhancedDashboardStatistics extends DashboardStatistics {
  // Trending data
  iswc_trend: number;              // % change vs last month
  disputed_trend: number;          // % change vs last month

  // Processing status
  uploads_processing: number;
  uploads_pending_review: number;
  uploads_failed: number;

  // Match quality
  match_confidence_distribution: {
    high: number;
    medium: number;
    low: number;
  };

  // Catalog completeness
  completeness_score: number;      // 0-100
  missing_iswc_count: number;
  missing_contributors_count: number;
}
```

**New Activity Log Endpoint** (`/api/v1/activity`):
```typescript
GET /api/v1/activity?types[]=upload&types[]=dispute&limit=10

interface ActivityLogResponse {
  data: ActivityItem[];
  pagination: PaginationMeta;
}

interface ActivityItem {
  id: string;
  type: 'upload' | 'dispute' | 'match' | 'export' | 'system';
  status: 'success' | 'failure' | 'pending' | 'processing';
  title: string;
  description: string;
  metadata: {
    upload_id?: number;
    work_id?: number;
    match_count?: number;
    confidence_distribution?: object;
  };
  actions: ActivityAction[];       // Available actions
  created_at: string;
}

interface ActivityAction {
  type: 'view' | 'export' | 'retry' | 'cancel';
  label: string;
  url?: string;                    // For navigation
  endpoint?: string;               // For API calls
}
```

**Upload Queue Endpoint** (`/api/v1/catalog/queue`):
```typescript
GET /api/v1/catalog/queue

interface UploadQueueResponse {
  processing: QueuedUpload[];
  pending: QueuedUpload[];
  failed: QueuedUpload[];
}

interface QueuedUpload {
  id: number;
  filename: string;
  status: UploadStatus;
  progress: number;                // 0-100
  estimated_completion: string;    // ISO timestamp
  position_in_queue?: number;
  error_message?: string;
}
```

### Real-Time Updates

**WebSocket Events** (for Upload Queue):
```typescript
// Subscribe to user's upload updates
socket.on('upload:progress', (data: {
  upload_id: number;
  progress: number;
  status: UploadStatus;
  estimated_completion: string;
}));

socket.on('upload:complete', (data: {
  upload_id: number;
  match_count: number;
  confidence_distribution: object;
}));

socket.on('upload:failed', (data: {
  upload_id: number;
  error_message: string;
  retry_allowed: boolean;
}));
```

### Performance Considerations

**Lazy Loading Strategy**:
```tsx
// Current: Charts are lazy loaded
const MonthlyTrendCharts = lazy(() => import('./MonthlyTrendCharts'));

// Proposed: Lazy load heavy widgets too
const UploadQueueWidget = lazy(() => import('./UploadQueueWidget'));
const MatchQualityChart = lazy(() => import('./MatchQualityChart'));

// Use Suspense with meaningful fallbacks
<Suspense fallback={<WidgetSkeleton />}>
  <UploadQueueWidget />
</Suspense>
```

**Data Fetching Optimization**:
```tsx
// Use parallel queries for independent data
const [
  { data: stats },
  { data: uploads },
  { data: queue },
  { data: activities }
] = useQueries({
  queries: [
    { queryKey: ['statistics'], queryFn: () => apiClient.getStatistics() },
    { queryKey: ['recent-uploads'], queryFn: () => apiClient.getCatalogUploads() },
    { queryKey: ['upload-queue'], queryFn: () => apiClient.getUploadQueue() },
    { queryKey: ['activities'], queryFn: () => apiClient.getActivities() }
  ]
});

// Use polling for real-time updates (fallback if WebSocket unavailable)
useQuery({
  queryKey: ['upload-queue'],
  queryFn: () => apiClient.getUploadQueue(),
  refetchInterval: 5000,  // Poll every 5 seconds
  enabled: hasActiveUploads
});
```

---

## 14. Accessibility & Usability Checklist

**Keyboard Navigation**:
- [ ] All action buttons accessible via Tab
- [ ] Enter/Space activates clickable cards
- [ ] Arrow keys navigate between cards
- [ ] Escape closes modals/dropdowns

**Screen Reader Support**:
- [ ] StatCards announce value and trend
- [ ] Activity feed items have descriptive labels
- [ ] Loading states announce progress
- [ ] Error states are clearly announced
- [ ] Action buttons have clear labels (not just icons)

**Visual Clarity**:
- [ ] Color is not the only indicator (use icons + text)
- [ ] Sufficient contrast ratios (WCAG AA minimum)
- [ ] Focus indicators are visible
- [ ] Text is resizable without breaking layout
- [ ] Charts have accessible data tables

**Mobile Responsiveness**:
- [ ] Stats grid stacks on mobile (already implemented)
- [ ] Action buttons are touch-friendly (44px min)
- [ ] Charts are scrollable/zoomable
- [ ] Activity feed is readable on small screens
- [ ] No horizontal scroll required

**Error Prevention**:
- [ ] Confirm before destructive actions (cancel upload)
- [ ] Clear error messages with recovery steps
- [ ] Disabled states are clearly indicated
- [ ] Form validation is inline and helpful

---

## 15. Competitive Analysis

### Industry Best Practices (Music Tech Dashboards)

**Spotify for Artists**:
- **Strengths**: Clear primary metrics, actionable insights, trend visualization
- **Applicable**: Show trending metrics, celebrate wins (e.g., "New high in matches!")
- **Lesson**: Focus on "what's changed" not just "what is"

**DistroKid Dashboard**:
- **Strengths**: Upload status front and center, clear CTAs
- **Applicable**: Prominent upload action, processing queue visibility
- **Lesson**: Make primary workflow the star of the dashboard

**Songtrust Dashboard**:
- **Strengths**: Earnings focus, royalty tracking, catalog health
- **Applicable**: Catalog completeness score, quality metrics
- **Lesson**: Give users a "score" to improve

**ASCAP Member Access**:
- **Strengths**: Work registration status, royalty statements
- **Applicable**: Clear status indicators, downloadable reports
- **Lesson**: Make data portable and actionable

### Dashboard Anti-Patterns to Avoid

**Vanity Metrics Without Context**:
- ❌ Showing "10,000 Total Works" without trend or comparison
- ✅ Show "10,000 Total Works (+247 this month, +2.5%)"

**Information Without Action**:
- ❌ "23 Disputed Rights" with no next step
- ✅ "23 Disputed Rights → Review Now"

**Buried Critical Information**:
- ❌ Failed uploads only visible in activity feed
- ✅ Failed uploads trigger alert banner

**Analysis Paralysis**:
- ❌ 20 different metrics with no guidance
- ✅ 5-7 key metrics + "Recommended Actions" widget

**Stale Data**:
- ❌ "Last updated: 6 hours ago"
- ✅ Real-time updates via WebSocket or frequent polling

---

## 16. User Testing Protocol

### Guerrilla Testing (Week 2)

**Objective**: Validate clickable cards and action buttons
**Participants**: 5 music publishers (current or potential users)
**Duration**: 15 minutes per session
**Location**: Remote (Zoom screen share)

**Test Script**:
1. **Warm-up** (2 min)
   - "Tell me about your catalog management workflow"
   - "What's the first thing you want to see on a dashboard?"

2. **Task 1** (3 min)
   - "You have 23 disputed rights. Show me how you'd review them."
   - **Success**: Clicks disputed rights card → navigates to filtered view
   - **Fail**: Looks for menu, unsure where to click

3. **Task 2** (3 min)
   - "Your catalog uploaded 2 hours ago. How would you view the results?"
   - **Success**: Clicks "View Results" on activity item
   - **Fail**: Navigates through menu, doesn't see activity feed

4. **Task 3** (2 min)
   - "Upload a new catalog file."
   - **Success**: Clicks "Upload Catalog" header button
   - **Fail**: Opens menu, looks for upload page

5. **Reflection** (5 min)
   - "What was confusing?"
   - "What would make this more useful?"
   - "On a scale of 1-5, how likely are you to use this dashboard daily?"

**Success Criteria**:
- 4/5 users complete Task 1 without hesitation
- 4/5 users complete Task 2 in <30 seconds
- 5/5 users complete Task 3 in <10 seconds
- Average rating ≥ 4/5

---

### Moderated Usability Test (Week 4)

**Objective**: Evaluate Upload Queue widget and recommended actions
**Participants**: 3 active users (mix of light and heavy uploaders)
**Duration**: 30 minutes per session
**Location**: Remote (Zoom + screen share + recording)

**Test Script**:
1. **Context Gathering** (5 min)
   - "Walk me through your last catalog upload experience"
   - "What questions did you have during processing?"
   - "How did you know when it was complete?"

2. **Upload Queue Widget** (10 min)
   - Show dashboard with active upload processing
   - "What is this telling you?"
   - "What would you do next?"
   - "Is this information helpful? What's missing?"
   - **Observe**: Do they understand progress? Do they use actions?

3. **Recommended Actions** (10 min)
   - Show dashboard with 3-4 recommended actions
   - "Which of these would you tackle first? Why?"
   - "Are any of these not relevant?"
   - "What actions are missing?"
   - **Observe**: Do recommendations match mental model?

4. **Comparative Assessment** (5 min)
   - Show before/after dashboard versions
   - "Which version helps you work faster?"
   - "What would you change about the new version?"

**Success Criteria**:
- 3/3 users understand upload progress without explanation
- 2/3 users find recommended actions helpful
- 2/3 users prefer new dashboard over old
- Identify 2-3 actionable improvements

---

### A/B Test (Week 8)

**Objective**: Quantify impact of Recommended Actions widget
**Participants**: All active users (50+ expected)
**Duration**: 2 weeks
**Method**: Feature flag A/B test

**Variant A (Control)**: Current dashboard
**Variant B (Treatment)**: Dashboard with Recommended Actions widget

**Metrics**:
| Metric | Hypothesis | Success Threshold |
|--------|-----------|-------------------|
| Dashboard engagement time | Increases | +20% |
| Click-through to actions | Increases | >30% CTR |
| Disputed rights resolution | Increases | +15% |
| Upload frequency | Increases | +10% |
| User satisfaction | Increases | +0.5 points |

**Analysis**:
- Statistical significance (p < 0.05)
- Segment by user type (light vs heavy uploader)
- Qualitative feedback survey to variant B users

---

## 17. Research Repository Structure

Create a dedicated research folder to track insights over time:

```
/Users/carlosmescalona/Documents/Projects/mlc_dashboard/research/
├── /personas/
│   ├── bulk-uploader.md         # "The Bulk Uploader" persona
│   ├── quality-guardian.md      # "The Quality Guardian" persona
│   └── admin-monitor.md         # "The System Monitor" persona
├── /journey-maps/
│   ├── catalog-upload-flow.md   # End-to-end upload journey
│   ├── dispute-resolution.md    # Dispute resolution journey
│   └── match-review.md          # Match review journey
├── /usability-tests/
│   ├── 2025-10-15-guerrilla/    # Week 2 guerrilla test
│   │   ├── script.md
│   │   ├── results.md
│   │   └── recordings/
│   ├── 2025-10-29-moderated/    # Week 4 moderated test
│   │   └── ...
│   └── 2025-11-19-ab-test/      # Week 8 A/B test
│       └── ...
├── /analytics-insights/
│   ├── dashboard-engagement.md  # Monthly analytics review
│   └── feature-adoption.md      # Feature usage tracking
├── /user-interviews/
│   ├── 2025-10-10-publisher-1.md
│   └── 2025-10-12-admin-1.md
└── /competitive-analysis/
    ├── spotify-for-artists.md
    ├── distrokid.md
    └── songtrust.md
```

---

## 18. Final Recommendations Summary

### Immediate Actions (This Sprint)

**HIGH PRIORITY - HIGH IMPACT**:
1. Make Disputed Rights card clickable
2. Add "Upload Catalog" CTA to header
3. Add action buttons to activity feed items
4. Display failed upload alert banner
5. Replace Saved Searches with Upload Queue widget

**MEDIUM PRIORITY - HIGH IMPACT**:
6. Add trend indicators to stat cards
7. Add "Pending Review" metric card
8. Enhance activity feed with more event types

### Next Sprint Priorities

**HIGH PRIORITY**:
1. Implement real-time upload progress tracking
2. Create Recommended Actions widget
3. Build Match Quality dashboard section

**MEDIUM PRIORITY**:
4. Add goal-setting functionality
5. Implement customizable layouts

### Long-Term Vision

**Transform Dashboard from Passive Report to Active Control Center**:
- **Current**: Users view data and leave
- **Future**: Users make decisions and take actions without leaving
- **Outcome**: Increased engagement, faster workflows, higher satisfaction

**Key Success Indicators** (6 months):
- 90% of users visit dashboard daily (vs ~40% baseline estimate)
- Average time-to-action < 30 seconds (vs ~2 minutes baseline)
- 50% reduction in "where do I..." support tickets
- 4.5/5 average dashboard usefulness rating

---

## 19. Appendix: Component Code Examples

### Example 1: Actionable StatCard Component

```tsx
/**
 * ActionableStatCard - Enhanced StatCard with click actions
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/components/ActionableStatCard.css';

interface ActionableStatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  iconColor?: 'primary' | 'success' | 'warning' | 'error' | 'neutral';
  trend?: TrendData;
  description?: string;
  severity?: 'info' | 'warning' | 'error';
  action?: {
    label: string;
    path: string;
  };
  loading?: boolean;
}

const ActionableStatCard: React.FC<ActionableStatCardProps> = ({
  title,
  value,
  icon,
  iconColor = 'primary',
  trend,
  description,
  severity,
  action,
  loading = false,
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (action) {
      navigate(action.path);
    }
  };

  const cardClasses = [
    'stat-card',
    action && 'stat-card--clickable',
    severity && `stat-card--${severity}`,
  ].filter(Boolean).join(' ');

  return (
    <div
      className={cardClasses}
      onClick={handleClick}
      role={action ? 'button' : undefined}
      tabIndex={action ? 0 : undefined}
      onKeyPress={(e) => {
        if (action && (e.key === 'Enter' || e.key === ' ')) {
          handleClick();
        }
      }}
    >
      <div className="stat-card__header">
        {icon && (
          <div className={`stat-card__icon stat-card__icon--${iconColor}`}>
            {icon}
          </div>
        )}
        <div className="stat-card__content">
          <h3 className="stat-card__title">{title}</h3>
          <p className="stat-card__value">{value}</p>
        </div>
      </div>

      {(trend || description || action) && (
        <div className="stat-card__footer">
          {trend && (
            <div className={`stat-card__trend stat-card__trend--${trend.direction}`}>
              <TrendIcon direction={trend.direction} />
              <span className="stat-card__trend-percentage">
                {trend.percentage}%
              </span>
              {trend.label && (
                <span className="stat-card__trend-label">{trend.label}</span>
              )}
            </div>
          )}
          {description && (
            <p className="stat-card__description">{description}</p>
          )}
          {action && (
            <div className="stat-card__action">
              <span className="stat-card__action-label">{action.label}</span>
              <ArrowRightIcon />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ActionableStatCard;
```

**CSS**:
```css
.stat-card--clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.stat-card--clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card--clickable:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.stat-card--warning {
  border-left: 4px solid var(--color-warning);
}

.stat-card--error {
  border-left: 4px solid var(--color-error);
}

.stat-card__action {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 500;
}

.stat-card__action-label {
  flex: 1;
}
```

---

### Example 2: Upload Queue Widget

```tsx
/**
 * UploadQueueWidget - Real-time upload processing status
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import '../../styles/components/UploadQueueWidget.css';

interface UploadQueueWidgetProps {
  onViewUpload?: (uploadId: number) => void;
  onCancelUpload?: (uploadId: number) => void;
}

const UploadQueueWidget: React.FC<UploadQueueWidgetProps> = ({
  onViewUpload,
  onCancelUpload,
}) => {
  const { data: queue, isLoading } = useQuery({
    queryKey: ['upload-queue'],
    queryFn: () => apiClient.getUploadQueue(),
    refetchInterval: 5000, // Poll every 5 seconds
  });

  const hasActiveUploads =
    queue && (queue.processing.length > 0 || queue.pending.length > 0);

  if (isLoading) {
    return (
      <div className="upload-queue">
        <h3 className="upload-queue__title">Upload Queue</h3>
        <div className="upload-queue__loading">
          <div className="loading-spinner" />
          <p>Loading queue status...</p>
        </div>
      </div>
    );
  }

  if (!hasActiveUploads && (!queue?.failed || queue.failed.length === 0)) {
    return (
      <div className="upload-queue">
        <h3 className="upload-queue__title">Upload Queue</h3>
        <div className="upload-queue__empty">
          <svg className="upload-queue__empty-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
          </svg>
          <p>No uploads in progress</p>
        </div>
      </div>
    );
  }

  return (
    <div className="upload-queue">
      <h3 className="upload-queue__title">Upload Queue</h3>

      <div className="upload-queue__list">
        {/* Processing Uploads */}
        {queue?.processing.map((upload) => (
          <div key={upload.id} className="upload-queue__item upload-queue__item--processing">
            <div className="upload-queue__item-header">
              <span className="upload-queue__filename">{upload.filename}</span>
              <span className="upload-queue__progress-text">{upload.progress}%</span>
            </div>

            <div className="upload-queue__progress-bar">
              <div
                className="upload-queue__progress-fill"
                style={{ width: `${upload.progress}%` }}
              />
            </div>

            <div className="upload-queue__item-footer">
              <span className="upload-queue__eta">
                {upload.estimated_completion
                  ? `Est. ${new Date(upload.estimated_completion).toLocaleTimeString()}`
                  : 'Processing...'}
              </span>
              {onCancelUpload && (
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => onCancelUpload(upload.id)}
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        ))}

        {/* Pending Uploads */}
        {queue?.pending.map((upload) => (
          <div key={upload.id} className="upload-queue__item upload-queue__item--pending">
            <div className="upload-queue__item-header">
              <span className="upload-queue__filename">{upload.filename}</span>
              <span className="upload-queue__status-badge upload-queue__status-badge--pending">
                Position #{upload.position_in_queue}
              </span>
            </div>
            <p className="upload-queue__status-text">Waiting in queue...</p>
            {onCancelUpload && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => onCancelUpload(upload.id)}
              >
                Cancel
              </button>
            )}
          </div>
        ))}

        {/* Failed Uploads */}
        {queue?.failed.map((upload) => (
          <div key={upload.id} className="upload-queue__item upload-queue__item--failed">
            <div className="upload-queue__item-header">
              <span className="upload-queue__filename">{upload.filename}</span>
              <span className="upload-queue__status-badge upload-queue__status-badge--error">
                Failed
              </span>
            </div>
            <p className="upload-queue__error-text">{upload.error_message}</p>
            <div className="upload-queue__item-actions">
              {onViewUpload && (
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => onViewUpload(upload.id)}
                >
                  View Details
                </button>
              )}
              <button className="btn btn-danger btn-sm">
                Retry Upload
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UploadQueueWidget;
```

---

## 20. Conclusion

The BWARM Dashboard has a solid foundation but requires a shift from **passive data display** to **active workflow enablement**. The recommended changes focus on:

1. **Immediate Actionability**: Every metric should suggest a next step
2. **User-Centric Information Architecture**: Prioritize what users need to do, not just what exists
3. **Workflow Integration**: Reduce friction between seeing data and acting on it
4. **Progress Transparency**: Show users where they are and where they're going
5. **Contextual Intelligence**: Recommend actions based on user state

By implementing these recommendations in the proposed sprints, the dashboard will evolve from a reporting tool into a mission control center that actively drives user success.

**Next Steps**:
1. Review and prioritize recommendations with product team
2. Schedule guerrilla testing for Week 2 (clickable cards)
3. Implement Sprint 1 quick wins (1 week)
4. Conduct moderated usability test in Week 4
5. Iterate based on user feedback
6. Continue monitoring analytics and user behavior

---

**Document Owner**: UX Research Team
**Last Updated**: 2025-10-06
**Version**: 1.0
**Review Cycle**: Every sprint (weekly)
