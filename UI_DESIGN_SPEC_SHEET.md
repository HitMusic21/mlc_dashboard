# MLC Dashboard - Visual Design Specification Sheet

**Version**: 1.0
**Date**: 2025-10-06
**Status**: Recommended Design System Enhancements

This specification sheet provides quick-reference design values for implementing the dashboard improvements.

---

## Color Palette Extensions

### Gradients (New)
```css
/* Primary Gradients */
--gradient-primary-main: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
--gradient-primary-light: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
--gradient-primary-subtle: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);

/* Card Background Gradients */
--gradient-card-light: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
--gradient-card-dark: linear-gradient(135deg, #1f2937 0%, #111827 100%);

/* Accent Gradients */
--gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
--gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
--gradient-error: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);

/* Shimmer Effect */
--gradient-shimmer: linear-gradient(90deg,
  transparent 0%,
  rgba(255, 255, 255, 0.1) 50%,
  transparent 100%
);

[data-theme="dark"] --gradient-shimmer: linear-gradient(90deg,
  transparent 0%,
  rgba(255, 255, 255, 0.05) 50%,
  transparent 100%
);
```

### Glass Morphism (New)
```css
/* Light Mode Glass */
--glass-bg-light: rgba(255, 255, 255, 0.9);
--glass-border-light: rgba(255, 255, 255, 0.2);
--glass-shadow-light: 0 8px 32px rgba(0, 0, 0, 0.1);
--glass-blur: blur(12px);

/* Dark Mode Glass */
--glass-bg-dark: rgba(31, 41, 55, 0.9);
--glass-border-dark: rgba(255, 255, 255, 0.1);
--glass-shadow-dark: 0 8px 32px rgba(0, 0, 0, 0.3);
```

### Overlay Colors (New)
```css
/* Radial Overlays for Card Depth */
--overlay-primary-light: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
--overlay-primary-dark: radial-gradient(circle, rgba(37, 99, 235, 0.15) 0%, transparent 70%);

--overlay-success-light: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
--overlay-success-dark: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%);

--overlay-warning-light: radial-gradient(circle, rgba(245, 158, 11, 0.1) 0%, transparent 70%);
--overlay-warning-dark: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%);
```

---

## Typography Scale Enhancements

### Font Sizes (Updated)
```css
--font-size-display: 3rem;        /* 48px - Hero sections */
--font-size-4xl: 2.5rem;          /* 40px - Page titles (increased) */
--font-size-3xl: 1.875rem;        /* 30px - Section titles */
--font-size-2xl: 1.5rem;          /* 24px - Card titles */
--font-size-xl: 1.25rem;          /* 20px - Subsections */
--font-size-lg: 1.125rem;         /* 18px - Large body */
--font-size-base: 1rem;           /* 16px - Default */
--font-size-sm: 0.875rem;         /* 14px - Small text */
--font-size-xs: 0.75rem;          /* 12px - Captions */
--font-size-tiny: 0.625rem;       /* 10px - Labels (new) */
```

### Letter Spacing (New)
```css
--letter-spacing-tighter: -0.03em;  /* Very tight headlines */
--letter-spacing-tight: -0.02em;    /* Tight headlines */
--letter-spacing-normal: 0;         /* Default */
--letter-spacing-wide: 0.05em;      /* Uppercase labels */
--letter-spacing-wider: 0.1em;      /* Extra wide labels */
```

### Line Heights (Enhanced)
```css
--line-height-none: 1;              /* For single-line titles */
--line-height-tight: 1.25;          /* Headlines */
--line-height-snug: 1.375;          /* Subheadings */
--line-height-normal: 1.5;          /* Body text */
--line-height-relaxed: 1.625;       /* Comfortable reading */
--line-height-loose: 2;             /* Very relaxed */
```

---

## Spacing System

### Base Spacing (Current)
```css
--spacing-0: 0;
--spacing-1: 0.25rem;    /* 4px */
--spacing-2: 0.5rem;     /* 8px */
--spacing-3: 0.75rem;    /* 12px */
--spacing-4: 1rem;       /* 16px */
--spacing-5: 1.25rem;    /* 20px */
--spacing-6: 1.5rem;     /* 24px */
--spacing-8: 2rem;       /* 32px */
--spacing-10: 2.5rem;    /* 40px */
--spacing-12: 3rem;      /* 48px */
--spacing-16: 4rem;      /* 64px */
--spacing-20: 5rem;      /* 80px */
```

### Component-Specific Spacing (Recommended)
```css
/* StatCard Spacing */
--stat-card-padding: var(--spacing-6);              /* 24px */
--stat-card-padding-mobile: var(--spacing-4);       /* 16px */
--stat-card-gap: var(--spacing-4);                  /* 16px */
--stat-card-icon-size: 56px;
--stat-card-icon-size-mobile: 44px;

/* Dashboard Spacing */
--dashboard-padding: var(--spacing-8);              /* 32px */
--dashboard-padding-mobile: var(--spacing-4);       /* 16px */
--dashboard-section-gap: var(--spacing-8);          /* 32px */
--dashboard-card-gap: var(--spacing-6);             /* 24px */
--dashboard-card-gap-mobile: var(--spacing-3);      /* 12px */

/* Grid Spacing */
--grid-gap-large: var(--spacing-6);                 /* 24px */
--grid-gap-medium: var(--spacing-4);                /* 16px */
--grid-gap-small: var(--spacing-3);                 /* 12px */
```

---

## Border Radius

### Base Radius (Current)
```css
--radius-none: 0;
--radius-sm: 0.125rem;    /* 2px */
--radius-base: 0.25rem;   /* 4px */
--radius-md: 0.375rem;    /* 6px */
--radius-lg: 0.5rem;      /* 8px */
--radius-xl: 0.75rem;     /* 12px */
--radius-2xl: 1rem;       /* 16px */
--radius-3xl: 1.5rem;     /* 24px - new */
--radius-full: 9999px;
```

### Component Radius (Recommended)
```css
--radius-button: var(--radius-lg);        /* 8px */
--radius-card: var(--radius-xl);          /* 12px - increased */
--radius-input: var(--radius-lg);         /* 8px */
--radius-icon: var(--radius-xl);          /* 12px */
--radius-badge: var(--radius-full);       /* pill shape */
--radius-modal: var(--radius-2xl);        /* 16px */
```

---

## Shadow System

### Base Shadows (Current + Enhanced)
```css
--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-base: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-md: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-lg: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
--shadow-xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
--shadow-2xl: 0 35px 60px -15px rgb(0 0 0 / 0.3);  /* new */
--shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
```

### Component Shadows (Recommended)
```css
/* Card Shadows */
--shadow-card-rest: var(--shadow-sm);
--shadow-card-hover: var(--shadow-lg);
--shadow-card-active: var(--shadow-xs);

/* Button Shadows */
--shadow-button-rest: var(--shadow-sm);
--shadow-button-hover: var(--shadow-md);

/* Modal/Overlay Shadows */
--shadow-modal: var(--shadow-2xl);
--shadow-dropdown: var(--shadow-lg);
```

### Dark Mode Shadows
```css
[data-theme="dark"] {
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.4);
  --shadow-base: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4);
  --shadow-md: 0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4);
  --shadow-xl: 0 25px 50px -12px rgb(0 0 0 / 0.5);
  --shadow-2xl: 0 35px 60px -15px rgb(0 0 0 / 0.6);
}
```

---

## Animation System

### Durations
```css
--duration-instant: 100ms;
--duration-fast: 150ms;
--duration-base: 200ms;
--duration-medium: 300ms;
--duration-slow: 500ms;
--duration-slower: 800ms;
```

### Easing Functions
```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
```

### Component Transitions (Recommended)
```css
/* StatCard Transitions */
--transition-card-hover: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-card-transform: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-card-shadow: box-shadow 200ms cubic-bezier(0.4, 0, 0.2, 1);

/* Button Transitions */
--transition-button: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-button-ripple: width 600ms, height 600ms;

/* Icon Transitions */
--transition-icon: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);

/* Background Transitions */
--transition-background: background-color 150ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Keyframe Animations
```css
/* Fade In Up */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Pulse Ring */
@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 0.1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

/* Skeleton Loading */
@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Skeleton Pulse */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Spin */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Shimmer */
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

---

## Component Specifications

### StatCard
```css
.stat-card {
  /* Layout */
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  padding: var(--spacing-6);

  /* Appearance */
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);

  /* Interaction */
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-200);
}

/* Gradient Overlay */
.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 150px;
  height: 150px;
  background: var(--overlay-primary-light);
  opacity: 0.3;
  pointer-events: none;
  transition: opacity var(--transition-base);
}

.stat-card:hover::before {
  opacity: 0.5;
}
```

### StatCard Icon
```css
.stat-card__icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-xl);
  transition: var(--transition-icon);
  position: relative;
}

.stat-card:hover .stat-card__icon {
  transform: scale(1.05);
}

/* Icon Color Variants */
.stat-card__icon--primary {
  background-color: var(--color-primary-100);
  color: var(--color-primary-600);
}

.stat-card__icon--success {
  background-color: var(--color-success-50);
  color: var(--color-success-700);
}

.stat-card__icon--warning {
  background-color: var(--color-warning-50);
  color: var(--color-warning-700);
}

.stat-card__icon--error {
  background-color: var(--color-error-50);
  color: var(--color-error-700);
}
```

### StatCard Typography
```css
.stat-card__title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--letter-spacing-wide);
  margin-bottom: var(--spacing-1);
}

.stat-card__value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: var(--line-height-tight);
  letter-spacing: var(--letter-spacing-tight);
}

.stat-card__description {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  line-height: var(--line-height-normal);
}
```

### Button Specifications
```css
.btn {
  /* Layout */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);

  /* Typography */
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-tight);

  /* Appearance */
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);

  /* Interaction */
  cursor: pointer;
  transition: var(--transition-button);
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background: var(--color-primary-600);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-700);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-lg {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
}

.btn-icon {
  width: 20px;
  height: 20px;
}
```

### Empty State
```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-12) var(--spacing-6);
  text-align: center;
  min-height: 300px;
}

.empty-state__icon-container {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary-subtle);
  border-radius: var(--radius-2xl);
  color: var(--color-primary-500);
  margin-bottom: var(--spacing-4);
}

.empty-state__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: var(--spacing-2);
}

.empty-state__description {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  max-width: 400px;
  margin-bottom: var(--spacing-6);
  line-height: var(--line-height-relaxed);
}
```

---

## Responsive Breakpoints

### Breakpoint Tokens
```css
/* Reference only - use in @media queries */
--breakpoint-xs: 375px;    /* Small mobile */
--breakpoint-sm: 640px;    /* Mobile */
--breakpoint-md: 768px;    /* Tablet */
--breakpoint-lg: 1024px;   /* Desktop */
--breakpoint-xl: 1280px;   /* Large desktop */
--breakpoint-2xl: 1536px;  /* Extra large desktop */
```

### Component Responsive Behavior

#### StatCard Grid
```css
/* Desktop (4 columns) */
@media (min-width: 1024px) {
  .dashboard__stats {
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-6);
  }
}

/* Tablet (2 columns) */
@media (min-width: 641px) and (max-width: 1023px) {
  .dashboard__stats {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-4);
  }
}

/* Mobile (2 columns, compact) */
@media (max-width: 640px) {
  .dashboard__stats {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-3);
  }

  .stat-card {
    padding: var(--spacing-4);
  }

  .stat-card__icon {
    width: 44px;
    height: 44px;
  }

  .stat-card__value {
    font-size: var(--font-size-2xl);
  }
}

/* Small Mobile (1 column if needed) */
@media (max-width: 375px) {
  .dashboard__stats {
    grid-template-columns: 1fr;
  }
}
```

---

## Accessibility Specifications

### Focus Indicators
```css
*:focus-visible {
  outline: 3px solid var(--color-primary-500);
  outline-offset: 4px;
  border-radius: inherit;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  *:focus-visible {
    outline-width: 4px;
    outline-style: dashed;
  }
}
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Color Contrast Requirements
```
Normal Text (16px+):     4.5:1 minimum (WCAG AA)
Large Text (24px+):      3:1 minimum (WCAG AA)
Icons/UI Components:     3:1 minimum (WCAG AA)

Current Status:
✓ Text Primary:   7.2:1 (Excellent)
✓ Text Secondary: 4.8:1 (Good)
✓ Text Tertiary:  4.5:1 (Minimum AA)
✓ Primary 600:    4.6:1 (Good)
```

### Touch Target Sizes
```
Minimum (WCAG):      44x44px
Recommended:         48x48px
Comfortable:         56x56px

Current Specs:
- Mobile Buttons:    44px min-height
- StatCard:          120px min-height (mobile)
- Activity Item:     72px min-height (mobile)
- Icon Buttons:      44x44px
```

---

## Performance Specifications

### Animation Performance
```
Target Frame Rate:       60fps (16.67ms per frame)
Max Frame Budget:        16ms
Animation Complexity:    Low (transforms & opacity only)
Hardware Acceleration:   Use transform & opacity for smooth 60fps
```

### Bundle Size Impact
```
CSS Addition:            ~15-20KB (minified & gzipped)
JavaScript Addition:     ~5KB (if number counting added)
Total Impact:            <30KB
Acceptable Threshold:    <50KB
```

### Loading Performance
```
First Paint:             <100ms
Time to Interactive:     <200ms
Skeleton Appearance:     <50ms
Animation Start:         After content render
Lazy Load Threshold:     500px before viewport
```

---

## Implementation Checklist

### Visual Polish
- [ ] Gradient backgrounds on StatCards
- [ ] Gradient header title
- [ ] Icon container shadows
- [ ] Hover lift effects
- [ ] Accent bar above header
- [ ] Enhanced button shadows

### Animations
- [ ] StatCard hover animations
- [ ] Icon pulse effects
- [ ] Button ripple effects
- [ ] Activity feed fade-in
- [ ] Skeleton shimmer
- [ ] Loading spinners

### Interactions
- [ ] Clickable StatCards
- [ ] Hover state feedback
- [ ] Active/pressed states
- [ ] Loading button states
- [ ] Disabled button states
- [ ] Touch-friendly targets

### Accessibility
- [ ] Focus indicators
- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Color contrast
- [ ] Reduced motion support

### Responsive
- [ ] Desktop 4-column grid
- [ ] Tablet 2-column grid
- [ ] Mobile 2-column grid
- [ ] Touch target sizes
- [ ] Comfortable spacing
- [ ] Landscape optimization

---

## Quick Reference Table

| Property | Desktop | Tablet | Mobile |
|----------|---------|--------|--------|
| **Dashboard Padding** | 32px | 24px | 16px |
| **Card Grid Columns** | 4 | 2 | 2 |
| **Card Grid Gap** | 24px | 16px | 12px |
| **Card Padding** | 24px | 20px | 16px |
| **Icon Size** | 56px | 48px | 44px |
| **Value Font Size** | 30px | 24px | 24px |
| **Min Touch Target** | - | 44px | 44px |

---

**End of Specification Sheet**

Use this document as a quick reference when implementing design improvements. For detailed implementation steps, refer to the Quick Start Guide.
