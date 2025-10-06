# Component Documentation

## Overview

The BWARM Dashboard frontend is built with React 19, TypeScript, and follows a component-based architecture with clear separation of concerns.

## Directory Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components (Button, Table, etc.)
│   ├── dashboard/      # Dashboard-specific components
│   ├── layout/         # Layout components (Header, Sidebar, etc.)
│   ├── notifications/  # Notification system components
│   ├── preferences/    # User preference components
│   └── ui/            # Base UI primitives
├── pages/             # Page-level components
├── stores/            # Zustand state management
├── services/          # API and external services
├── styles/            # CSS styles
└── types/             # TypeScript type definitions
```

## Core Components

### Layout Components

#### Header (`/components/layout/Header.tsx`)
Main navigation header with user menu, notifications, and mobile navigation.

**Props:**
```typescript
interface HeaderProps {
  user: UserResponse | null;
  onLogout: () => void;
  className?: string;
}
```

**Features:**
- Notification dropdown with unread count badge
- User dropdown menu (Profile, Preferences, Dashboard Layout, Logout)
- Mobile hamburger menu integration
- Theme-aware styling

**Usage:**
```tsx
<Header
  user={currentUser}
  onLogout={handleLogout}
  className="custom-header"
/>
```

#### MobileNav (`/components/layout/MobileNav.tsx`)
Mobile navigation drawer with hamburger menu.

**Props:**
```typescript
interface MobileNavProps {
  user: UserResponse | null;
  isOpen: boolean;
  onClose: () => void;
}
```

**Features:**
- Slide-in drawer animation
- Touch-friendly 56px tap targets
- User profile section
- Active route highlighting
- Safe area inset support for iOS notch

**Usage:**
```tsx
<MobileNav
  user={user}
  isOpen={isMobileNavOpen}
  onClose={() => setIsMobileNavOpen(false)}
/>
```

#### Layout (`/components/layout/Layout.tsx`)
Main application layout wrapper.

**Features:**
- Responsive sidebar
- Header integration
- Content area with proper spacing
- Mobile-optimized layout

### Dashboard Components

#### StatCard (`/components/dashboard/StatCard.tsx`)
Displays a statistic with title, value, and optional trend.

**Props:**
```typescript
interface StatCardProps {
  title: string;
  value: number | string;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  className?: string;
}
```

**Usage:**
```tsx
<StatCard
  title="Total Works"
  value={1500}
  change={12}
  changeLabel="from last month"
  icon={<DocumentIcon />}
/>
```

#### ChartsPanel (`/components/dashboard/ChartsPanel.tsx`)
Recharts-based visualization panel with responsive design.

**Props:**
```typescript
interface ChartsPanelProps {
  data: ChartDataPoint[];
  type: 'line' | 'bar' | 'pie';
  title?: string;
  height?: number;
}
```

**Features:**
- Line, bar, and pie chart support
- Responsive sizing
- Tooltip interactions
- Color-coded by theme

**Usage:**
```tsx
<ChartsPanel
  data={chartData}
  type="line"
  title="Match Trends"
  height={300}
/>
```

#### ActivityFeed (`/components/dashboard/ActivityFeed.tsx`)
Real-time activity log display.

**Props:**
```typescript
interface ActivityFeedProps {
  activities: ActivityItem[];
  loading?: boolean;
  onLoadMore?: () => void;
}

interface ActivityItem {
  id: string;
  user_email?: string;
  action: string;
  description: string;
  status: 'success' | 'failure' | 'pending';
  created_at: string;
}
```

**Features:**
- Status indicators (success, failure, pending)
- Relative timestamps ("2 hours ago")
- Load more pagination
- Empty state handling

### Notification Components

#### NotificationDropdown (`/components/notifications/NotificationDropdown.tsx`)
Header notification dropdown with recent notifications.

**Props:**
```typescript
interface NotificationDropdownProps {
  notifications: NotificationItem[];
  unreadCount: number;
  onMarkAsRead: (id: string) => void;
  onMarkAllAsRead: () => void;
  onViewAll: () => void;
}
```

**Features:**
- Unread count badge
- Mark as read/Mark all as read
- View all link to full notifications page
- Click outside to close
- Keyboard navigation (ESC to close)

#### Toast (`/components/notifications/Toast.tsx`)
Temporary notification toast component.

**Props:**
```typescript
interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;  // 0 = no auto-dismiss
  onClose: (id: string) => void;
}
```

**Features:**
- Auto-dismiss with configurable duration
- Progress bar animation
- Type-based styling (success=green, error=red, etc.)
- Enter/exit animations
- Mobile-optimized positioning

**Usage:**
```tsx
const { showToast } = useToast();

showToast({
  type: 'success',
  title: 'Success',
  message: 'Work matched successfully',
  duration: 3000
});
```

#### ToastProvider (`/components/notifications/ToastContainer.tsx`)
Global toast management context.

**Context API:**
```typescript
interface ToastContextValue {
  showToast: (options: Omit<ToastProps, 'id' | 'onClose'>) => void;
  showSuccess: (title: string, message?: string) => void;
  showError: (title: string, message?: string) => void;
  showWarning: (title: string, message?: string) => void;
  showInfo: (title: string, message?: string) => void;
}

const { showSuccess, showError } = useToast();
```

### Preference Components

#### PreferencesModal (`/components/preferences/PreferencesModal.tsx`)
User preferences configuration modal.

**Props:**
```typescript
interface PreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Features:**
- Theme selection (Light, Dark, Auto)
- Items per page configuration
- Save/Cancel actions
- Persists to user preferences API

#### DashboardLayoutEditor (`/components/preferences/DashboardLayoutEditor.tsx`)
Visual dashboard widget customization.

**Props:**
```typescript
interface DashboardLayoutEditorProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Features:**
- Widget palette (Stats, Charts, Activity, Notifications, Saved Searches)
- Add/remove widgets
- Move up/down positioning
- Resize widget width
- Preview layout changes
- Save/reset functionality

**Widget Types:**
```typescript
type WidgetType = 'stat' | 'chart' | 'activity' | 'notifications' | 'searches';

interface DashboardWidget {
  id: string;
  type: WidgetType;
  position: {
    x: number;
    y: number;
    w: number;  // width (1-12 columns)
    h: number;  // height
  };
}
```

### Common Components

#### VirtualizedTable (`/components/common/VirtualizedTable.tsx`)
High-performance table with windowing for large datasets.

**Props:**
```typescript
interface VirtualizedTableProps<T> {
  data: T[];
  columns: Column<T>[];
  height?: number;
  rowHeight?: number;
  onRowClick?: (row: T) => void;
}

interface Column<T> {
  key: string;
  label: string;
  width?: number;
  render?: (value: any, row: T) => React.ReactNode;
}
```

**Features:**
- Windowing for 1000+ rows
- Custom cell renderers
- Sortable columns
- Row selection
- Responsive width

**Usage:**
```tsx
<VirtualizedTable
  data={works}
  columns={[
    { key: 'title', label: 'Title', width: 300 },
    { key: 'writer', label: 'Writer', width: 200 },
    {
      key: 'status',
      label: 'Status',
      render: (value) => <StatusBadge status={value} />
    }
  ]}
  height={600}
  rowHeight={50}
  onRowClick={(work) => navigate(`/works/${work.id}`)}
/>
```

## Page Components

### Dashboard (`/pages/Dashboard.tsx`)
Main dashboard with statistics, charts, and activity feed.

**Features:**
- Statistics cards (Total Works, Matched, Pending, Unmatched)
- Interactive charts (Match trends, confidence distribution)
- Recent activity feed
- Quick actions panel
- Saved searches shortcuts

### WorksBrowser (`/pages/WorksBrowser.tsx`)
Browse and search musical works.

**Features:**
- Virtualized table for performance
- Advanced search and filters
- Bulk selection and actions
- Export functionality
- Pagination with user preference support

### CatalogMatcher (`/pages/CatalogMatcher.tsx`)
Search and match works to catalog entries.

**Features:**
- Catalog search with fuzzy matching
- Confidence score visualization
- Accept/reject match actions
- Bulk matching operations
- Match comparison view

### NotificationsPage (`/pages/NotificationsPage.tsx`)
Full notification management page.

**Features:**
- All/Unread tabs
- Mark as read/delete actions
- Clear all read notifications
- Expandable notification details
- Action links to related entities
- Empty state handling

## State Management (Zustand)

### usePreferencesStore
Manages user preferences with persistence.

**State:**
```typescript
{
  preferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;
}
```

**Actions:**
```typescript
{
  fetchPreferences: () => Promise<void>;
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>;
  setTheme: (theme: ThemePreference) => Promise<void>;
  setDashboardLayout: (layout: DashboardLayoutConfig) => Promise<void>;
  setItemsPerPage: (count: number) => Promise<void>;
}
```

**Selectors:**
```typescript
const selectTheme = (state) => state.preferences?.theme ?? 'auto';
const selectItemsPerPage = (state) => state.preferences?.items_per_page ?? 50;
const selectDashboardLayout = (state) => state.preferences?.dashboard_layout;
```

### useNotificationsStore
Manages notifications state.

**State:**
```typescript
{
  notifications: Notification[];
  unreadCount: number;
  total: number;
  page: number;
  limit: number;
  isLoading: boolean;
  error: string | null;
}
```

**Actions:**
```typescript
{
  fetchNotifications: (params?: NotificationParams) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  clearReadNotifications: () => Promise<void>;
}
```

## Styling

### CSS Architecture
- **tokens.css**: Design tokens (colors, spacing, typography)
- **global.css**: Global resets and base styles
- **typography.css**: Text styles and hierarchy
- **layout.css**: Layout utilities and grid system
- **components.css**: Base component styles
- **mobile.css**: Mobile-first responsive utilities

### Theme System
Themes are controlled via `data-theme` attribute on `<html>`:
- `data-theme="light"`: Light mode
- `data-theme="dark"`: Dark mode
- Auto theme: Detects system preference

**CSS Custom Properties:**
```css
:root[data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-text-primary: #1a1a1a;
}

:root[data-theme="dark"] {
  --color-bg-primary: #1a1a1a;
  --color-text-primary: #ffffff;
}
```

### Responsive Design
Mobile-first approach with breakpoints:
- `sm`: 640px (Mobile landscape, small tablets)
- `md`: 768px (Tablets)
- `lg`: 1024px (Desktop)
- `xl`: 1280px (Large desktop)
- `2xl`: 1536px (Extra large)

**Utility Classes:**
- `.hidden-mobile`: Hide on mobile
- `.mobile-only`: Show only on mobile
- `.tablet-up-only`: Show on tablet and up
- `.desktop-up-only`: Show on desktop and up

## Best Practices

### Component Guidelines
1. **Props validation**: Use TypeScript interfaces for all props
2. **Default props**: Provide sensible defaults
3. **Error boundaries**: Wrap risky components
4. **Loading states**: Show skeletons/spinners during data fetch
5. **Empty states**: Handle no-data scenarios gracefully
6. **Accessibility**: Include ARIA labels, keyboard navigation

### Performance
1. **Lazy loading**: Use React.lazy() for route components
2. **Memoization**: Use React.memo() for expensive renders
3. **Virtualization**: Use VirtualizedTable for large lists
4. **Code splitting**: Separate vendor and page chunks

### Testing
1. **Unit tests**: Test component logic in isolation
2. **Integration tests**: Test component interactions
3. **E2E tests**: Use Playwright for full user flows
4. **Accessibility tests**: Ensure WCAG 2.1 compliance

---

**Last Updated**: 2024-01-15
**Framework**: React 19 + TypeScript
**Styling**: CSS Modules + Custom Properties
