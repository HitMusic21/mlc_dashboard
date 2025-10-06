# Quick Reference: Dashboard Features Checklist
## MLC Dashboard - 6-Day Sprint Priorities

**Last Updated:** October 5, 2025

---

## Must-Have Features (Days 1-6)

### Core Layout & Design
- [ ] **Responsive Grid System** - 12-column layout (mobile/tablet/desktop)
- [ ] **Dark Mode Toggle** - User preference with LocalStorage persistence
- [ ] **Clean, Minimalist UI** - Maximum 3-4 colors, ample white space
- [ ] **Mobile-First Design** - Touch targets 44x44px minimum

### Essential Widgets (6-8 total)
- [ ] **KPI Cards** (4x) - Total streams, monthly listeners, followers, playlists
  - Trend indicators (up/down arrows + percentage)
  - 7-day sparklines
- [ ] **Streaming Timeline** - Line chart with 7D/28D/3M/1Y options
- [ ] **Top Tracks Table** - Sortable, shows top 5-10 tracks
- [ ] **Platform Distribution** - Donut chart (Spotify, Apple Music, YouTube, etc.)
- [ ] **Geographic Heatmap** - World map with listener concentration
- [ ] **Activity Feed** - Recent events (playlist adds, milestones)

### Interactivity
- [ ] **Hover Tooltips** - Detailed breakdowns on chart hover
- [ ] **Date Range Picker** - Global filter affecting all widgets
- [ ] **Platform Filter** - Filter by streaming service
- [ ] **Click-to-Filter** - Click chart elements to drill down
- [ ] **Export Charts** - Download as PNG/SVG

### Real-Time Features
- [ ] **Auto-Refresh** - Polling every 30-60 seconds OR WebSocket
- [ ] **Last Updated Timestamp** - Show data freshness
- [ ] **Smooth Transitions** - Animated number counters, fade-in new data
- [ ] **Toast Notifications** - Important events (playlist adds, milestones)

---

## Recommended Tech Stack

### Frontend
```bash
# Core
npm install react react-dom
npm install -D typescript @types/react @types/react-dom

# Styling
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Charts
npm install recharts

# State & Data
npm install zustand @tanstack/react-query

# Utilities
npm install date-fns clsx
npm install react-hot-toast
npm install framer-motion

# Real-Time (choose one)
npm install socket.io-client
# OR use polling with React Query
```

### Backend Additions
```bash
# Real-Time
pip install python-socketio redis

# AI/ML (optional)
pip install openai scikit-learn pandas numpy
```

---

## Widget Priority Matrix

### Priority 1 (Critical - Days 1-3)
1. KPI Cards with trends
2. Streaming timeline chart
3. Top tracks table
4. Platform distribution chart
5. Responsive layout + dark mode

### Priority 2 (Important - Days 4-5)
6. Geographic heatmap
7. Activity feed
8. Real-time updates (polling)
9. Interactive filtering
10. Date range selector

### Priority 3 (Nice-to-Have - Day 6 or Post-MVP)
11. WebSocket real-time (vs polling)
12. Drag-and-drop widget rearrangement
13. AI-generated insights
14. Natural language search
15. Export/share features

---

## Color Palette

### Light Mode
```css
--bg-primary: #FFFFFF
--bg-secondary: #F9FAFB
--text-primary: #111827
--text-secondary: #6B7280
--border: #E5E7EB
```

### Dark Mode
```css
--bg-primary: #121212
--bg-secondary: #1F2937
--text-primary: #F3F4F6
--text-secondary: #9CA3AF
--border: #374151
```

### Accent Colors (Both Modes)
```css
--primary: #6366F1 (Indigo)
--success: #10B981 (Green)
--warning: #F59E0B (Amber)
--error: #EF4444 (Red)
```

---

## Chart Types by Use Case

| Data Type | Best Chart | Library | Priority |
|-----------|-----------|---------|----------|
| Streams over time | Line chart | Recharts.LineChart | P1 |
| Top tracks ranking | Bar chart | Recharts.BarChart | P1 |
| Platform split | Donut chart | Recharts.PieChart | P1 |
| Geographic data | Heatmap | react-map-gl | P2 |
| Demographics | Stacked bar | Recharts.BarChart | P2 |
| Trend in KPI card | Sparkline | Recharts.Sparkline | P1 |
| Playlist growth | Area chart | Recharts.AreaChart | P2 |

---

## Key Metrics to Display

### Primary Metrics (KPI Cards)
1. **Total Streams** - All-time or selected period
2. **Monthly Listeners** - Active listeners in last 28 days
3. **Followers** - Total follower count across platforms
4. **Playlist Count** - Number of playlists featuring tracks

### Secondary Metrics (Charts & Tables)
- Stream velocity (growth rate %)
- Top tracks by streams
- Platform breakdown (Spotify, Apple Music, YouTube, etc.)
- Geographic distribution (top countries)
- Playlist reach (total potential audience)
- Demographic breakdown (age, gender)

### Activity Feed Events
- Playlist additions/removals
- Follower milestones (10K, 50K, 100K, etc.)
- Streaming milestones
- Peak listener count records
- New chart entries

---

## Mobile Optimizations

### Layout Changes
- **Desktop:** 3-4 columns, all widgets visible
- **Tablet:** 2 columns, some widgets collapsible
- **Mobile:** 1 column, priority-based ordering

### Mobile-First Widget Order
1. Date range picker (sticky header)
2. Key metrics (4x KPI cards in 2x2 grid)
3. Streaming timeline (simplified to 7 days)
4. Top 3 tracks (vs 10 on desktop)
5. Platform chart (full width)
6. Activity feed (last 5 events)
7. Other widgets (collapsible sections)

### Touch Gestures
- Swipe left/right to change date ranges
- Pull-to-refresh for manual updates
- Tap-and-hold for widget options
- Pinch-to-zoom on charts (optional)

---

## Real-Time Implementation Options

### Option 1: Polling (Simpler - Recommended for MVP)
```javascript
// Using React Query
const { data } = useQuery({
  queryKey: ['streams'],
  queryFn: fetchStreams,
  refetchInterval: 30000, // 30 seconds
});
```

### Option 2: WebSocket (More Scalable - Post-MVP)
```javascript
// Using Socket.io
useEffect(() => {
  socket.on('stream_update', (data) => {
    setStreams(data);
  });
  return () => socket.off('stream_update');
}, []);
```

**Recommendation:** Start with polling, migrate to WebSocket in Phase 2.

---

## Performance Checklist

- [ ] Lazy load charts below the fold
- [ ] Implement virtual scrolling for long tables
- [ ] Use React.memo for expensive components
- [ ] Debounce filter inputs (300ms)
- [ ] Cache API responses (React Query)
- [ ] Code split routes and large components
- [ ] Optimize images (WebP, responsive sizes)
- [ ] Use CSS animations (GPU-accelerated) over JS

---

## Accessibility Checklist

- [ ] Keyboard navigation support (Tab, Enter, Esc)
- [ ] ARIA labels for charts and interactive elements
- [ ] Alt text for all images and icons
- [ ] Color contrast ratio ≥ 4.5:1 (WCAG AA)
- [ ] Focus indicators on all interactive elements
- [ ] Screen reader-friendly table structure
- [ ] Skip to content link
- [ ] Reduced motion preference support

---

## Quick Win Differentiators

**vs Spotify for Artists:**
- Natural language search ("show my top track in Brazil")
- Customizable widget layouts
- AI-generated insights

**vs Chartmetric:**
- Cleaner, modern UI with glassmorphism
- Free tier with core features
- Faster real-time updates

**vs TuneCore:**
- Better mobile experience
- More interactive visualizations
- Dark mode support

---

## Launch Checklist (End of Day 6)

### Functionality
- [ ] All 6-8 core widgets working
- [ ] Real-time updates active (polling minimum)
- [ ] Responsive on mobile, tablet, desktop
- [ ] Dark mode functional
- [ ] No console errors
- [ ] Loading states for all async operations
- [ ] Error handling for failed API calls

### Polish
- [ ] Smooth animations and transitions
- [ ] Consistent spacing and alignment
- [ ] Proper typography hierarchy
- [ ] Hover states on all interactive elements
- [ ] Empty states with helpful messaging
- [ ] Loading skeletons (vs spinners)

### Testing
- [ ] Test on Chrome, Safari, Firefox
- [ ] Test on iOS Safari and Android Chrome
- [ ] Test with slow network (3G throttling)
- [ ] Test with sample data edge cases (0 streams, huge numbers)
- [ ] Test dark mode on all pages
- [ ] Test keyboard navigation

---

## Example Component Structure

```
src/
├── components/
│   ├── dashboard/
│   │   ├── DashboardGrid.tsx
│   │   ├── KPICard.tsx
│   │   ├── StreamingChart.tsx
│   │   ├── TopTracksTable.tsx
│   │   ├── PlatformChart.tsx
│   │   ├── GeographicMap.tsx
│   │   └── ActivityFeed.tsx
│   ├── shared/
│   │   ├── DateRangePicker.tsx
│   │   ├── ThemeToggle.tsx
│   │   ├── FilterBar.tsx
│   │   └── LoadingSkeleton.tsx
│   └── charts/
│       ├── LineChart.tsx
│       ├── BarChart.tsx
│       ├── DonutChart.tsx
│       └── Sparkline.tsx
├── hooks/
│   ├── useStreams.ts
│   ├── useRealTime.ts
│   └── useTheme.ts
├── lib/
│   ├── api.ts
│   ├── utils.ts
│   └── constants.ts
└── types/
    └── index.ts
```

---

## Daily Sprint Goals

### Day 1: Foundation
- Set up Tailwind CSS
- Create grid layout component
- Build KPI card component
- Implement theme toggle

### Day 2: Basic Charts
- Install Recharts
- Build streaming timeline chart
- Build top tracks bar chart
- Build platform donut chart

### Day 3: Interactivity
- Add tooltips to all charts
- Implement date range picker
- Add click-to-filter interactions
- Create filter bar component

### Day 4: Advanced Widgets
- Build geographic heatmap
- Create activity feed component
- Add demographic charts
- Build top tracks table

### Day 5: Real-Time
- Implement polling or WebSocket
- Add toast notification system
- Create smooth update animations
- Add "last updated" timestamps

### Day 6: Polish & Testing
- Mobile responsive testing
- Performance optimization
- Error handling
- Loading states
- Documentation

---

## Key Resources

**Documentation:**
- Recharts: https://recharts.org/
- Tailwind CSS: https://tailwindcss.com/
- React Query: https://tanstack.com/query/
- Socket.io: https://socket.io/docs/

**Design Inspiration:**
- Spotify for Artists dashboard
- Dribbble: "dark dashboard" search
- Chartmetric platform
- YouTube Studio Analytics

**Full Research:**
See `DASHBOARD_TRENDS_RESEARCH_2025.md` for comprehensive findings.

---

**Quick Reference Version:** 1.0
**For Full Details:** See DASHBOARD_TRENDS_RESEARCH_2025.md
