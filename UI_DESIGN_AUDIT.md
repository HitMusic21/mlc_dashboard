# BWARM Dashboard UI Design Audit
**Comprehensive Visual Design Analysis & Recommendations**

## Executive Summary

The BWARM Dashboard frontend demonstrates a solid functional foundation with clean component architecture. However, it currently lacks a cohesive visual design system, consistent styling patterns, and modern UI polish. This audit provides actionable recommendations to transform the application into a visually stunning, professionally designed dashboard that users will love to share.

**Current State**: Functional but visually incomplete (NO CSS implementation found)
**Design Approach**: Class-based styling with semantic naming conventions
**CSS Architecture**: Currently NONE - all styles are referenced but not implemented
**Component Quality**: Well-structured React components with accessibility considerations

---

## 1. Visual Design System Analysis

### Current State: CRITICAL GAPS

**Problems Identified:**
- ❌ **No CSS implementation** - Only `index.css` exists with basic Vite defaults
- ❌ No color system defined
- ❌ No typography scale implemented
- ❌ No spacing/layout grid system
- ❌ No component-level styling
- ❌ Heavy reliance on class names with zero visual implementation

**Component Classes Used (but not styled):**
```css
/* Pages */
.login-page, .dashboard-page, .works-browser-page
.catalog-matcher-page, .results-viewer-page, .admin-page

/* Layout */
.app-layout, .app-header, .sidebar, .layout-main

/* Components */
.stat-card, .upload-card, .action-card, .modal-backdrop
.virtualized-table, .search-bar, .filter-panel
.upload-progress, .confidence-indicator
```

### Recommended Design System Foundation

#### Color Palette (Modern, Professional, TikTok-Ready)

```css
/* Primary Brand Colors */
--color-primary-50: #EEF2FF;
--color-primary-100: #E0E7FF;
--color-primary-200: #C7D2FE;
--color-primary-300: #A5B4FC;
--color-primary-400: #818CF8;
--color-primary-500: #6366F1;  /* Main brand color */
--color-primary-600: #4F46E5;
--color-primary-700: #4338CA;
--color-primary-800: #3730A3;
--color-primary-900: #312E81;

/* Secondary/Accent */
--color-accent-400: #34D399;  /* Success green */
--color-accent-500: #10B981;
--color-accent-600: #059669;

/* Warning/Medium Confidence */
--color-warning-400: #FBBF24;
--color-warning-500: #F59E0B;
--color-warning-600: #D97706;

/* Error/Danger */
--color-error-400: #F87171;
--color-error-500: #EF4444;
--color-error-600: #DC2626;

/* Neutral/Grayscale */
--color-gray-50: #F9FAFB;
--color-gray-100: #F3F4F6;
--color-gray-200: #E5E7EB;
--color-gray-300: #D1D5DB;
--color-gray-400: #9CA3AF;
--color-gray-500: #6B7280;
--color-gray-600: #4B5563;
--color-gray-700: #374151;
--color-gray-800: #1F2937;
--color-gray-900: #111827;

/* Background & Surface */
--bg-primary: #FFFFFF;
--bg-secondary: #F9FAFB;
--bg-tertiary: #F3F4F6;
--surface-elevated: #FFFFFF;
--surface-overlay: rgba(17, 24, 39, 0.5);

/* Text Colors */
--text-primary: #111827;
--text-secondary: #6B7280;
--text-tertiary: #9CA3AF;
--text-inverse: #FFFFFF;
```

#### Typography System

```css
/* Font Families */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
             'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

/* Font Sizes (Mobile-first) */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
--text-5xl: 3rem;        /* 48px */

/* Line Heights */
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### Spacing System (8px base grid)

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

#### Border Radius

```css
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.375rem;  /* 6px */
--radius-lg: 0.5rem;    /* 8px */
--radius-xl: 0.75rem;   /* 12px */
--radius-2xl: 1rem;     /* 16px */
--radius-3xl: 1.5rem;   /* 24px */
--radius-full: 9999px;
```

#### Shadows (Elevated, Modern)

```css
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
             0 1px 2px -1px rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 8px 10px -6px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Colored Shadows for Visual Pop */
--shadow-primary: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
--shadow-success: 0 10px 25px -5px rgba(16, 185, 129, 0.3);
--shadow-error: 0 10px 25px -5px rgba(239, 68, 68, 0.3);
```

---

## 2. Component Design Breakdown & Recommendations

### 2.1 Login Page (`Login.tsx`)

**Current Implementation:**
- Clean semantic structure
- Inline SVG logo
- Form validation states
- Loading spinner

**Design Recommendations:**

```css
/* Login Page Styling */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary-600) 0%, var(--color-primary-800) 100%);
  padding: var(--space-4);
}

.login-container {
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  padding: var(--space-10);
  max-width: 420px;
  width: 100%;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.login-logo {
  color: var(--color-primary-600);
  margin-bottom: var(--space-4);
  width: 64px;
  height: 64px;
  margin-left: auto;
  margin-right: auto;
}

.login-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.login-subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.form-input {
  padding: var(--space-3) var(--space-4);
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  transition: all 0.2s ease;
  background: var(--bg-primary);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.login-button {
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary-600);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.login-button:hover:not(:disabled) {
  background: var(--color-primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-primary);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--color-error-200);
  border-radius: var(--radius-lg);
  color: var(--color-error-700);
  font-size: var(--text-sm);
}

.button-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.demo-credentials {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-align: center;
  padding: var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  margin-top: var(--space-6);
}
```

**Visual Enhancements:**
1. **Gradient background** - Modern, eye-catching
2. **Glass morphism card** - Trending design pattern
3. **Smooth micro-interactions** - Button hover/press states
4. **Colored shadows** - Adds depth and visual interest
5. **Focus states** - Clear, accessible input highlighting

---

### 2.2 Layout Components

#### Header (`Header.tsx`)

**Design Recommendations:**

```css
.app-header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 40;
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.9);
}

.header-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-6);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.brand-logo {
  color: var(--color-primary-600);
  width: 40px;
  height: 40px;
}

.brand-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-800));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.nav-link {
  padding: var(--space-2) var(--space-4);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  text-decoration: none;
  position: relative;
}

.nav-link:hover {
  color: var(--color-primary-600);
  background: var(--color-primary-50);
}

.nav-link.active {
  color: var(--color-primary-600);
  background: var(--color-primary-50);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: var(--space-4);
  right: var(--space-4);
  height: 2px;
  background: var(--color-primary-600);
  border-radius: var(--radius-full);
}

.header-user {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  border: none;
  background: transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-button:hover {
  background: var(--bg-secondary);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-700));
  color: var(--text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.user-role {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-transform: capitalize;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  min-width: 240px;
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--space-2);
  z-index: 50;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: none;
  background: transparent;
  text-align: left;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.dropdown-item:hover {
  background: var(--bg-secondary);
  color: var(--color-primary-600);
}
```

#### Sidebar (`Sidebar.tsx`)

```css
.sidebar {
  width: 240px;
  background: var(--bg-primary);
  border-right: 1px solid var(--color-gray-200);
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  padding: var(--space-6) 0;
}

.sidebar.closed {
  width: 72px;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: 0 var(--space-3);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  background: var(--color-gray-100);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-primary-600);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sidebar.closed .nav-label {
  display: none;
}

.sidebar-collapse {
  margin: var(--space-4) var(--space-3);
  padding: var(--space-2);
  border: 1px solid var(--color-gray-300);
  background: transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-collapse:hover {
  background: var(--bg-secondary);
  border-color: var(--color-gray-400);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 30;
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
```

---

### 2.3 Dashboard Components

#### Statistics Cards

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stat-card {
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  transition: all 0.3s ease;
  cursor: default;
}

.stat-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
  border-color: var(--color-primary-200);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.works {
  background: linear-gradient(135deg, var(--color-primary-100), var(--color-primary-200));
  color: var(--color-primary-600);
}

.stat-icon.iswc {
  background: linear-gradient(135deg, var(--color-accent-100), var(--color-accent-200));
  color: var(--color-accent-600);
}

.stat-icon.disputed {
  background: linear-gradient(135deg, var(--color-warning-100), var(--color-warning-200));
  color: var(--color-warning-600);
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stat-percentage {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
```

#### Action Cards

```css
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-4);
}

.action-card {
  background: var(--bg-primary);
  border: 2px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-700));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.action-card:hover {
  border-color: var(--color-primary-400);
  box-shadow: var(--shadow-xl), var(--shadow-primary);
  transform: translateY(-4px);
}

.action-card:hover::before {
  transform: scaleX(1);
}

.action-icon {
  width: 40px;
  height: 40px;
  color: var(--color-primary-600);
  transition: all 0.3s ease;
}

.action-card:hover .action-icon {
  transform: scale(1.1) rotate(5deg);
}

.action-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.action-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}
```

---

### 2.4 Table Components (`VirtualizedTable.tsx`)

```css
.virtualized-table {
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.table-header {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 2px solid var(--color-gray-300);
  padding: var(--space-3) var(--space-4);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-header-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0 var(--space-3);
  transition: all 0.2s ease;
}

.table-header-cell.sortable {
  cursor: pointer;
  user-select: none;
}

.table-header-cell.sortable:hover {
  color: var(--color-primary-600);
}

.table-header-cell.sorted-asc,
.table-header-cell.sorted-desc {
  color: var(--color-primary-600);
}

.sort-indicator {
  font-size: var(--text-lg);
  line-height: 1;
}

.sort-placeholder {
  opacity: 0.3;
}

.table-row {
  display: flex;
  border-bottom: 1px solid var(--color-gray-200);
  padding: var(--space-3) var(--space-4);
  transition: all 0.15s ease;
}

.table-row.clickable {
  cursor: pointer;
}

.table-row:hover {
  background: var(--color-gray-50);
}

.table-row.clickable:hover {
  background: var(--color-primary-50);
}

.table-cell {
  display: flex;
  align-items: center;
  padding: 0 var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.text-muted {
  color: var(--text-tertiary);
  font-style: italic;
}

/* Code elements (ISWC, IPI) */
code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--color-gray-100);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  color: var(--color-primary-700);
  font-weight: var(--font-medium);
}
```

---

### 2.5 Form Components

#### Search Bar

```css
.search-bar {
  width: 100%;
  max-width: 600px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--space-4);
  color: var(--text-tertiary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--space-3) var(--space-12) var(--space-3) var(--space-12);
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-xl);
  font-size: var(--text-base);
  transition: all 0.2s ease;
  background: var(--bg-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.clear-button {
  position: absolute;
  right: var(--space-3);
  padding: var(--space-2);
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-button:hover {
  background: var(--color-gray-200);
  color: var(--text-primary);
}
```

#### Filter Panel

```css
.filter-panel {
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.filter-panel-toggle {
  width: 100%;
  padding: var(--space-4);
  border: none;
  background: var(--bg-secondary);
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s ease;
}

.filter-panel-toggle:hover {
  background: var(--color-gray-200);
}

.filter-panel-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.active-indicator {
  color: var(--color-primary-600);
}

.toggle-icon {
  transition: transform 0.3s ease;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.filter-panel-content {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.filter-section-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.filter-checkbox:hover {
  background: var(--bg-secondary);
}

.filter-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--color-gray-400);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-checkbox input[type="checkbox"]:checked {
  background: var(--color-primary-600);
  border-color: var(--color-primary-600);
}

.filter-date-input {
  padding: var(--space-2) var(--space-3);
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  transition: all 0.2s ease;
}

.filter-date-input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.filter-actions {
  display: flex;
  gap: var(--space-2);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-gray-200);
}

.filter-button {
  flex: 1;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.apply-button {
  background: var(--color-primary-600);
  color: var(--text-inverse);
}

.apply-button:hover:not(:disabled) {
  background: var(--color-primary-700);
}

.reset-button {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--color-gray-300);
}

.reset-button:hover:not(:disabled) {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.filter-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

### 2.6 Upload Components

#### File Uploader (Drag & Drop)

```css
.file-uploader {
  width: 100%;
}

.dropzone {
  border: 2px dashed var(--color-gray-300);
  border-radius: var(--radius-2xl);
  padding: var(--space-12);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-secondary);
}

.dropzone:hover:not(.disabled) {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
}

.dropzone.drag-active {
  border-color: var(--color-primary-600);
  background: var(--color-primary-100);
  transform: scale(1.02);
}

.dropzone.has-file {
  border-color: var(--color-accent-400);
  background: var(--color-accent-50);
  border-style: solid;
}

.dropzone.error {
  border-color: var(--color-error-400);
  background: var(--color-error-50);
}

.dropzone.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.upload-icon,
.file-icon {
  width: 64px;
  height: 64px;
  color: var(--color-gray-400);
}

.file-icon.success {
  color: var(--color-accent-500);
}

.dropzone-message {
  font-size: var(--text-base);
  color: var(--text-primary);
}

.primary-text {
  color: var(--color-primary-600);
  font-weight: var(--font-semibold);
}

.dropzone-hint {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.file-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.file-size {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.upload-error {
  margin-top: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-error-50);
  border: 1px solid var(--color-error-200);
  border-radius: var(--radius-lg);
  color: var(--color-error-700);
  font-size: var(--text-sm);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
```

#### Upload Progress

```css
.upload-progress {
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  margin-top: var(--space-4);
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.status-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.status-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.status-icon.loading {
  animation: spin 1s linear infinite;
}

.status-icon.success {
  color: var(--color-accent-500);
}

.status-icon.error {
  color: var(--color-error-500);
}

.status-label {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.progress-bar-container {
  width: 100%;
  height: 8px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-4);
}

.progress-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
  position: relative;
  overflow: hidden;
}

.progress-bar.blue {
  background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-600));
}

.progress-bar.green {
  background: linear-gradient(90deg, var(--color-accent-500), var(--color-accent-600));
}

.progress-bar.red {
  background: linear-gradient(90deg, var(--color-error-500), var(--color-error-600));
}

/* Animated shimmer effect */
.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.progress-stats {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.progress-percentage {
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-size: var(--text-lg);
}

.tracks-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.time-remaining {
  color: var(--text-tertiary);
  font-style: italic;
}

.cancel-button {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-error-300);
  background: transparent;
  color: var(--color-error-600);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background: var(--color-error-50);
  border-color: var(--color-error-500);
}
```

---

### 2.7 Confidence Indicator

```css
.confidence-indicator {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.confidence-indicator.size-small {
  gap: var(--space-1);
}

.confidence-indicator.size-large {
  gap: var(--space-3);
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.confidence-indicator.confidence-high .confidence-badge {
  background: var(--color-accent-100);
  color: var(--color-accent-700);
}

.confidence-indicator.confidence-medium .confidence-badge {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.confidence-indicator.confidence-low .confidence-badge {
  background: var(--color-gray-200);
  color: var(--color-gray-700);
}

.confidence-bar {
  width: 100%;
  height: 6px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.confidence-indicator.confidence-high .confidence-fill {
  background: linear-gradient(90deg, var(--color-accent-500), var(--color-accent-600));
}

.confidence-indicator.confidence-medium .confidence-fill {
  background: linear-gradient(90deg, var(--color-warning-500), var(--color-warning-600));
}

.confidence-indicator.confidence-low .confidence-fill {
  background: linear-gradient(90deg, var(--color-gray-400), var(--color-gray-500));
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--color-primary-100);
  color: var(--color-primary-700);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}
```

---

### 2.8 Modal Components

```css
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--surface-overlay);
  backdrop-filter: blur(4px);
  z-index: 50;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content,
.match-details-modal,
.work-details-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  z-index: 51;
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, -45%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-gray-200);
  flex-shrink: 0;
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.modal-close:hover {
  background: var(--color-gray-100);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.modal-section {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-4);
}

.details-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: var(--space-3);
}

.detail-row dt {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.detail-row dd {
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin: 0;
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-gray-200);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  flex-shrink: 0;
}
```

---

### 2.9 Badge Components

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge.success {
  background: var(--color-accent-100);
  color: var(--color-accent-700);
}

.badge.warning {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.badge.required {
  background: var(--color-error-100);
  color: var(--color-error-700);
}

.badge.optional {
  background: var(--color-gray-100);
  color: var(--color-gray-700);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.status-badge.status-completed {
  background: var(--color-accent-100);
  color: var(--color-accent-700);
}

.status-badge.status-processing {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.status-badge.status-failed {
  background: var(--color-error-100);
  color: var(--color-error-700);
}

.status-badge.status-uploading {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.status-badge.status-active {
  background: var(--color-accent-100);
  color: var(--color-accent-700);
}

.status-badge.status-inactive {
  background: var(--color-gray-100);
  color: var(--color-gray-700);
}

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: capitalize;
}

.role-badge.role-admin {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.role-badge.role-publisher {
  background: var(--color-accent-100);
  color: var(--color-accent-700);
}
```

---

### 2.10 Button System

```css
/* Primary Buttons */
.button-primary,
.login-button,
.upload-button {
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary-600);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  text-decoration: none;
}

.button-primary:hover:not(:disabled) {
  background: var(--color-primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-primary);
}

.button-primary:active:not(:disabled) {
  transform: translateY(0);
}

.button-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Secondary Buttons */
.button-secondary {
  padding: var(--space-3) var(--space-6);
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.button-secondary:hover:not(:disabled) {
  background: var(--bg-secondary);
  border-color: var(--color-gray-400);
}

.button-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Danger Buttons */
.button-danger {
  padding: var(--space-3) var(--space-6);
  background: var(--color-error-600);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-danger:hover:not(:disabled) {
  background: var(--color-error-700);
  box-shadow: var(--shadow-error);
}

.button-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-danger-small {
  padding: var(--space-1) var(--space-3);
  background: transparent;
  color: var(--color-error-600);
  border: 1px solid var(--color-error-300);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-danger-small:hover:not(:disabled) {
  background: var(--color-error-50);
  border-color: var(--color-error-500);
}

/* Link Buttons */
.button-link {
  padding: var(--space-1) var(--space-2);
  background: transparent;
  color: var(--color-primary-600);
  border: none;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.button-link:hover {
  color: var(--color-primary-700);
  text-decoration: underline;
}
```

---

## 3. Page-Level Layout Patterns

### Global Layout Structure

```css
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

.layout-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-8) var(--space-6);
}

/* Page Headers */
.page-header {
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  line-height: 1.2;
}

.page-subtitle {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  margin: 0;
}

/* Section Headers */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.section-link {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-primary-600);
  text-decoration: none;
  transition: all 0.2s ease;
}

.section-link:hover {
  color: var(--color-primary-700);
}

/* Cards */
.section-card {
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}
```

### Pagination

```css
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
  padding: var(--space-4);
}

.pagination-button {
  padding: var(--space-2) var(--space-4);
  background: var(--bg-primary);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-button:hover:not(:disabled) {
  background: var(--color-primary-50);
  border-color: var(--color-primary-400);
  color: var(--color-primary-600);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}
```

---

## 4. Loading & Empty States

```css
/* Loading States */
.app-loading,
.dashboard-loading,
.loading-fallback,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: var(--space-4);
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.spinner-icon {
  animation: spin 1s linear infinite;
  color: var(--color-primary-600);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
}

/* Empty States */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
  color: var(--text-secondary);
}

.empty-state p {
  margin-bottom: var(--space-4);
  font-size: var(--text-base);
}

/* Error States */
.error-boundary,
.error-page,
.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
}

.error-content {
  max-width: 400px;
}

.error-icon {
  color: var(--color-error-500);
  margin-bottom: var(--space-4);
}

.error-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.error-message {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

.error-button {
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary-600);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-lg);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-button:hover {
  background: var(--color-primary-700);
}
```

---

## 5. Responsive Design Patterns

```css
/* Mobile First Breakpoints */
@media (max-width: 640px) {
  .page-title {
    font-size: var(--text-3xl);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .header-nav {
    display: none; /* Show in mobile menu */
  }

  .layout-main {
    padding: var(--space-4);
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Desktop enhancements */
@media (min-width: 1280px) {
  .layout-main {
    padding: var(--space-12) var(--space-10);
  }

  .page-title {
    font-size: var(--text-5xl);
  }
}
```

---

## 6. Micro-Interactions & Animations

### Hover Effects

```css
/* Smooth hover transitions on interactive elements */
.action-card,
.stat-card,
.upload-card,
.nav-item,
.button-primary,
.button-secondary {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Scale on hover for cards */
.stat-card:hover,
.action-card:hover {
  transform: translateY(-2px) scale(1.01);
}

/* Pulse animation for loading states */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  background: linear-gradient(
    90deg,
    var(--color-gray-200) 25%,
    var(--color-gray-300) 50%,
    var(--color-gray-200) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}
```

### Focus States (Accessibility)

```css
/* Global focus ring */
*:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Remove default browser outline */
*:focus {
  outline: none;
}

/* Custom focus for interactive elements */
.button-primary:focus-visible,
.button-secondary:focus-visible,
.form-input:focus-visible,
.search-input:focus-visible {
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}
```

---

## 7. Dark Mode Support (Future Enhancement)

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Dark mode color overrides */
    --bg-primary: #1F2937;
    --bg-secondary: #111827;
    --bg-tertiary: #0F172A;
    --surface-elevated: #374151;
    --surface-overlay: rgba(0, 0, 0, 0.75);

    --text-primary: #F9FAFB;
    --text-secondary: #D1D5DB;
    --text-tertiary: #9CA3AF;
    --text-inverse: #111827;

    /* Adjust borders for dark mode */
    --color-gray-200: #374151;
    --color-gray-300: #4B5563;
  }
}
```

---

## 8. Performance Optimizations

### CSS Best Practices Implemented

1. **Use CSS Custom Properties** - Easy theming and consistency
2. **Minimize Reflows** - Transform and opacity for animations
3. **Will-change for animations** - GPU acceleration
4. **Contain property** - Layout containment for better performance

```css
/* Performance optimizations */
.modal-backdrop,
.modal-content {
  will-change: opacity, transform;
}

.virtualized-table {
  contain: layout style paint;
}

.table-row {
  contain: layout paint;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 9. Icon System

**Recommendation**: Use inline SVGs (as currently implemented) for:
- Custom control
- Better styling flexibility
- No external dependencies
- Smaller bundle size

**Enhance with:**
```css
.icon {
  width: 1em;
  height: 1em;
  display: inline-block;
  fill: currentColor;
  vertical-align: middle;
}

.icon-sm { font-size: 16px; }
.icon-md { font-size: 20px; }
.icon-lg { font-size: 24px; }
.icon-xl { font-size: 32px; }
```

---

## 10. Implementation Priority

### Phase 1: Foundation (Week 1)
1. ✅ Set up CSS custom properties (design tokens)
2. ✅ Implement global reset and base styles
3. ✅ Create typography system
4. ✅ Build button component styles
5. ✅ Implement form input styles

### Phase 2: Layout & Navigation (Week 2)
1. ✅ Header styling
2. ✅ Sidebar styling
3. ✅ Page layout grid
4. ✅ Responsive breakpoints

### Phase 3: Components (Week 3-4)
1. ✅ Cards (stat, upload, action)
2. ✅ Tables (virtualized)
3. ✅ Modals and overlays
4. ✅ Search and filters
5. ✅ Upload components
6. ✅ Progress indicators
7. ✅ Badges and labels

### Phase 4: Polish & Animations (Week 5)
1. ✅ Micro-interactions
2. ✅ Loading states
3. ✅ Empty states
4. ✅ Error states
5. ✅ Accessibility refinements

### Phase 5: Optimization (Week 6)
1. ✅ Performance audit
2. ✅ Bundle size optimization
3. ✅ Browser compatibility testing
4. ✅ Accessibility audit (WCAG 2.1 AA)

---

## 11. Key Recommendations Summary

### Visual Design System
1. **Implement CSS custom properties** - Full design token system
2. **Use modern color palette** - Vibrant, professional, screenshot-worthy
3. **Establish 8px spacing grid** - Consistent, predictable layouts
4. **Create typography scale** - Clear hierarchy, excellent readability

### Component Patterns
1. **Card-based layouts** - Flexible, mobile-friendly
2. **Floating action patterns** - Clear CTAs
3. **Progressive disclosure** - Collapse/expand for dense data
4. **Consistent hover states** - Visual feedback everywhere

### Modern Enhancements
1. **Glass morphism** - Login, modals, elevated surfaces
2. **Gradient accents** - Brand elements, CTAs
3. **Subtle shadows** - Depth and elevation
4. **Smooth animations** - 200-300ms transitions
5. **Colored shadows** - Primary buttons, success states

### Accessibility
1. **WCAG 2.1 AA compliant** - Color contrast, focus states
2. **Keyboard navigation** - Full support
3. **Screen reader support** - ARIA labels, semantic HTML
4. **Reduced motion** - Respect user preferences

### Performance
1. **CSS custom properties** - Fast theme switching
2. **GPU-accelerated animations** - Transform and opacity
3. **Layout containment** - Prevent reflows
4. **Minimal dependencies** - Inline SVGs, no icon libraries

---

## 12. File Structure Recommendation

```
frontend/src/styles/
├── tokens/
│   ├── colors.css          # Color system
│   ├── typography.css      # Font system
│   ├── spacing.css         # Spacing scale
│   ├── shadows.css         # Shadow system
│   └── borders.css         # Border radius, widths
├── base/
│   ├── reset.css           # CSS reset
│   ├── typography.css      # Global typography
│   └── utilities.css       # Utility classes
├── components/
│   ├── buttons.css
│   ├── forms.css
│   ├── cards.css
│   ├── tables.css
│   ├── modals.css
│   ├── badges.css
│   └── [component].css
├── layout/
│   ├── header.css
│   ├── sidebar.css
│   ├── page.css
│   └── grid.css
└── themes/
    ├── light.css           # Light theme (default)
    └── dark.css            # Dark mode overrides
```

---

## 13. TikTok-Ready Design Features

To make the dashboard "screenshot-worthy" and shareable:

1. **Vibrant color combinations** - Eye-catching gradients
2. **Bold typography** - Clear hierarchy, standout numbers
3. **Colorful data visualization** - Charts that pop
4. **Animated success states** - Confetti, checkmarks, celebrations
5. **Beautiful empty states** - Engaging illustrations
6. **Smooth transitions** - Delightful micro-interactions
7. **Hero moments** - Upload completion, match results
8. **Clean, modern aesthetic** - Professional yet approachable

---

## Conclusion

The BWARM Dashboard has **excellent functional bones** but needs **complete visual implementation**. The component architecture is solid, accessibility is considered, and the semantic class naming is perfect for styling.

**Critical Next Step**: Create a comprehensive CSS stylesheet implementing all design tokens and component styles outlined in this audit.

**Expected Outcome**: Transform from functional prototype to visually stunning, professional dashboard that users will be proud to share and competitors will envy.

**Time to Implementation**: 4-6 weeks for full design system
**Quick Win**: 1 week for foundation + login page + header to demonstrate visual direction

---

**Files Referenced in Audit:**
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/index.css`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/App.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/pages/Login.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/pages/Dashboard.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/pages/WorksBrowser.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/pages/CatalogMatcher.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/pages/ResultsViewer.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/pages/Admin.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/layout/Layout.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/layout/Header.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/layout/Sidebar.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/common/SearchBar.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/common/FilterPanel.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/common/VirtualizedTable.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/common/ExportButton.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/upload/FileUploader.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/upload/UploadProgress.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/upload/FormatValidator.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/results/MatchResults.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/results/MatchDetailsModal.tsx`
- `/Users/carlosmescalona/Documents/Projects/mlc_dashboard/frontend/src/components/results/ConfidenceIndicator.tsx`
