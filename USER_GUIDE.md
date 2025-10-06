# BWARM Dashboard User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Works Browser](#works-browser)
4. [Catalog Matcher](#catalog-matcher)
5. [Notifications](#notifications)
6. [User Preferences](#user-preferences)
7. [Admin Features](#admin-features)
8. [Mobile App](#mobile-app)
9. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### Logging In

1. Navigate to the BWARM Dashboard URL
2. Enter your email address and password
3. Click "Sign In"

> **First-time users**: Contact your administrator to create an account.

### Dashboard Layout

The dashboard consists of:
- **Header**: Navigation, notifications, user menu
- **Sidebar**: Main navigation menu (Desktop)
- **Content Area**: Current page content
- **Mobile Menu**: Hamburger icon on mobile devices

---

## Dashboard Overview

The main dashboard provides a comprehensive view of your works and matching activities.

### Statistics Cards

At the top of the dashboard, you'll find key metrics:
- **Total Works**: All works in the system
- **Matched Works**: Successfully matched to catalog
- **Pending Works**: Awaiting manual review
- **Unmatched Works**: No catalog matches found

**Tip**: Click on any stat card to filter the works list by that status.

### Charts Panel

Visual representations of your data:
- **Match Trends**: Line chart showing matching activity over time
- **Confidence Distribution**: Bar chart of match confidence scores
- **Status Breakdown**: Pie chart of work statuses

**Tip**: Hover over chart elements for detailed tooltips.

### Activity Feed

Real-time updates on system activities:
- Catalog uploads
- Match completions
- User actions
- System events

**Color coding**:
- 🟢 Green: Success
- 🔴 Red: Failure
- 🟡 Yellow: Pending

### Quick Actions

Access frequently used features:
- Upload new catalog
- Browse pending works
- View recent matches
- Export data

---

## Works Browser

Manage and search your musical works catalog.

### Searching Works

1. Navigate to "Browse Works" from the sidebar
2. Use the search bar to find works by:
   - Title
   - Writer/Composer name
   - Work ID
   - ISWC code

**Advanced Search**:
- Click "Advanced" to access additional filters
- Combine multiple search criteria
- Save frequently used searches

### Filtering Works

Filter works by:
- **Status**: Matched, Pending, Unmatched
- **Confidence Score**: Set minimum threshold (0-100%)
- **Date Range**: Created or updated dates
- **Publisher**: Filter by publisher name

**Applying Filters**:
1. Click the "Filter" button
2. Select your criteria
3. Click "Apply Filters"
4. View filtered results

**Tip**: Active filters are shown as badges. Click the X to remove.

### Sorting Results

Sort works by clicking column headers:
- **Title**: Alphabetical order
- **Writer**: Composer/Writer name
- **Status**: Match status
- **Created Date**: Newest or oldest first
- **Confidence Score**: Highest or lowest match

Click once for ascending, twice for descending order.

### Viewing Work Details

To view full work information:
1. Click on any work row
2. View detailed information panel:
   - Basic info (title, writer, ISWC)
   - Match details
   - Metadata
   - Match history

### Bulk Actions

Select multiple works for batch operations:
1. Click checkboxes next to works
2. Or click "Select All" header checkbox
3. Choose bulk action:
   - Export selected
   - Bulk match
   - Change status
   - Delete (Admin only)

---

## Catalog Matcher

Find and confirm matches between your works and catalog entries.

### Searching for Matches

1. Navigate to "Catalog Matcher"
2. Enter search query:
   - Work title
   - Composer name
   - ISWC code
3. Click "Search" or press Enter

**Search Tips**:
- Use partial names for broader results
- Include multiple identifying details
- Try different spelling variations

### Understanding Match Results

Each match result shows:
- **Catalog Entry**: Title, composer, publisher
- **Confidence Score**: Match accuracy (0-100%)
- **Match Reasons**: Why this was suggested
  - Exact ISWC match
  - Title similarity percentage
  - Composer match
  - Metadata alignment

**Confidence Score Guide**:
- 90-100%: Highly confident (likely exact match)
- 70-89%: Confident (probable match)
- 50-69%: Moderate (requires review)
- Below 50%: Low confidence (unlikely match)

### Accepting a Match

To confirm a match:
1. Review match details carefully
2. Verify title, composer, and ISWC
3. Click "Accept Match"
4. Confirm in the dialog

**Result**: Work status changes to "Matched" and is linked to catalog entry.

### Rejecting a Match

If a match is incorrect:
1. Click "Reject" on the match
2. Optionally add rejection reason
3. Confirm rejection

**Result**: Match is removed from suggestions. You can search for alternative matches.

### Comparing Multiple Matches

When multiple potential matches are found:
1. Click "Compare" button
2. View side-by-side comparison:
   - Title variations
   - Composer details
   - Confidence scores
   - Metadata differences
3. Select the best match
4. Click "Accept" on chosen match

### Bulk Matching

For high-confidence matches:
1. Set confidence threshold (e.g., 95%)
2. Click "Auto-Match High Confidence"
3. Review proposed matches
4. Confirm bulk accept

**Warning**: Use bulk matching carefully. Always verify a sample before accepting large batches.

---

## Notifications

Stay informed about important events and updates.

### Notification Types

- 🔵 **Info**: General information (Blue)
- 🟢 **Success**: Completed actions (Green)
- 🟡 **Warning**: Requires attention (Yellow)
- 🔴 **Error**: Failed actions (Red)

### Accessing Notifications

**Header Dropdown**:
1. Click bell icon in header
2. View 5 most recent notifications
3. Click "View All" for full list

**Notifications Page**:
1. Click "Notifications" in sidebar
2. Or click "View All" from dropdown
3. See complete notification history

### Managing Notifications

**Mark as Read**:
- Click notification to expand
- Click "Mark as Read" button
- Or click "Mark All as Read" for all

**Delete Notifications**:
- Click trash icon on individual notification
- Or click "Clear Read" to remove all read

**Filter Notifications**:
- **All**: View everything
- **Unread**: Only unread notifications

### Notification Actions

Some notifications include action links:
- **View Work**: Opens related work details
- **Review Match**: Go to catalog matcher
- **View Upload**: Check catalog upload status

Click the action link to navigate directly.

---

## User Preferences

Customize your dashboard experience.

### Accessing Preferences

1. Click user avatar in header
2. Select "Preferences" from dropdown
3. Or use keyboard shortcut: `Ctrl/Cmd + ,`

### Theme Settings

Choose your visual theme:
- **Light**: Bright, high-contrast interface
- **Dark**: Low-light friendly, reduced eye strain
- **Auto**: Follows system preference

**Changing Theme**:
1. Open Preferences
2. Click desired theme option
3. Preview changes in real-time
4. Click "Save"

**Tip**: Auto theme adjusts automatically when your system changes between light/dark mode.

### Items Per Page

Control how many items display in lists:
- Options: 25, 50, 100, 200
- Default: 50

**Setting Items Per Page**:
1. Open Preferences
2. Select from dropdown
3. Click "Save"
4. All tables update immediately

### Dashboard Layout

Customize your dashboard widgets.

**Opening Layout Editor**:
1. Click user avatar
2. Select "Dashboard Layout"

**Available Widgets**:
- 📊 **Statistics Cards**: Key metrics summary
- 📈 **Charts Panel**: Visual data representation
- 📋 **Activity Feed**: Recent actions log
- 🔔 **Notifications**: Recent notifications
- 🔍 **Saved Searches**: Quick search access

**Customizing Layout**:
1. Click widget in palette to add
2. Use ↑↓ arrows to reorder
3. Adjust width slider for sizing
4. Click X to remove widget
5. Click "Save Layout" when done

**Reset to Default**:
- Click "Reset to Default" button
- Confirms before resetting

### Saved Searches

Save frequently used search filters.

**Creating Saved Search**:
1. Configure filters in Works Browser
2. Click "Save Search"
3. Name your search
4. Click "Save"

**Using Saved Searches**:
1. Open Preferences
2. View saved searches list
3. Click search to apply

**Managing Saved Searches**:
- Edit: Update filters
- Delete: Remove saved search
- Reorder: Drag to rearrange

---

## Admin Features

Administrative functions for system management.

> **Note**: Admin features require admin role permissions.

### User Management

Manage user accounts and permissions.

**Adding Users**:
1. Navigate to "Admin" → "Users"
2. Click "Add User"
3. Enter user details:
   - Email address
   - Role (Admin, User)
   - Initial password
4. Click "Create User"

**Managing Existing Users**:
- **Edit**: Update user details
- **Deactivate**: Temporarily disable access
- **Delete**: Permanently remove user
- **Reset Password**: Generate new password

### Catalog Upload

Upload new catalog files for matching.

**Supported Formats**:
- CSV (Comma-separated values)
- Excel (.xlsx, .xls)

**File Requirements**:
- Required columns: Title, Composer, ISWC
- Optional: Publisher, Year, Duration, Genre
- Max file size: 50 MB

**Uploading Catalog**:
1. Navigate to "Admin" → "Catalog"
2. Click "Upload Catalog"
3. Select file
4. Enter publisher name (optional)
5. Click "Upload"
6. Monitor processing status

**Processing Status**:
- 🔵 **Pending**: Queued for processing
- 🟡 **Processing**: Currently being processed
- 🟢 **Completed**: Successfully processed
- 🔴 **Failed**: Processing error

**Viewing Upload History**:
1. Click "Catalog Uploads" tab
2. View all past uploads
3. Filter by status or date
4. Download error logs for failed uploads

### System Monitoring

Monitor system health and performance.

**Activity Logs**:
- View all user actions
- Filter by user, action type, date
- Export logs for auditing

**Performance Metrics**:
- API response times
- Database query performance
- Cache hit rates
- Error rates

### Configuration

System-wide settings and configuration.

**Matching Settings**:
- Confidence threshold defaults
- Auto-matching rules
- Fuzzy matching sensitivity

**Notification Settings**:
- Email notification templates
- Webhook configurations
- Alert thresholds

**Security Settings**:
- Session timeout duration
- Password requirements
- Two-factor authentication

---

## Mobile App

Access BWARM Dashboard on mobile devices.

### Mobile Features

Full-featured mobile experience:
- ✅ All core functionality
- ✅ Touch-optimized interface
- ✅ Swipe gestures
- ✅ Offline support (coming soon)

### Mobile Navigation

**Hamburger Menu**:
1. Tap hamburger icon (☰) in header
2. Access all main sections
3. Tap outside to close

**Bottom Navigation** (on some screens):
- Quick access to key features
- Swipe between tabs

### Mobile-Optimized Features

**Virtualized Tables**:
- Card-based layout on mobile
- Swipe to reveal actions
- Pull-to-refresh

**Touch Gestures**:
- Swipe left: Delete/Archive
- Swipe right: Mark as read
- Long press: Select multiple

**Mobile Filters**:
- Tap "Filter" button
- Drawer slides up from bottom
- Apply filters
- Swipe down to close

### Installing as PWA

Install dashboard as a mobile app:

**iOS (Safari)**:
1. Open dashboard in Safari
2. Tap Share button
3. Select "Add to Home Screen"
4. Tap "Add"

**Android (Chrome)**:
1. Open dashboard in Chrome
2. Tap menu (⋮)
3. Select "Add to Home screen"
4. Tap "Add"

**Benefits**:
- App icon on home screen
- Full-screen experience
- Faster loading
- Offline access (future)

---

## Tips & Tricks

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Quick search |
| `Ctrl/Cmd + ,` | Open preferences |
| `Ctrl/Cmd + /` | Show shortcuts |
| `Esc` | Close modal/dropdown |
| `?` | Help menu |

### Performance Tips

**Faster Loading**:
- Use filters to limit results
- Increase items per page for fewer loads
- Bookmark frequently used filters

**Efficient Searching**:
- Use specific search terms
- Combine multiple filters
- Save common searches

**Batch Operations**:
- Select multiple items at once
- Use bulk actions for efficiency
- Export data for offline analysis

### Best Practices

**Catalog Matching**:
1. Review high-confidence matches first (90%+)
2. Use comparison view for similar matches
3. Add notes when rejecting matches
4. Regularly review pending works

**Data Quality**:
1. Keep work metadata up-to-date
2. Verify ISWC codes
3. Standardize composer names
4. Use consistent formatting

**Security**:
1. Log out when finished
2. Don't share credentials
3. Use strong passwords
4. Enable 2FA if available

### Common Issues

**Can't Find a Work**:
- Check spelling
- Try partial search
- Clear filters
- Use advanced search

**Match Not Appearing**:
- Lower confidence threshold
- Try alternative search terms
- Check catalog is uploaded
- Contact support

**Slow Performance**:
- Reduce results with filters
- Clear browser cache
- Check internet connection
- Use fewer active widgets

### Getting Help

**In-App Help**:
- Click "?" icon for contextual help
- Hover tooltips on icons
- Read notification messages

**Support Resources**:
- Email: support@bwarm.com
- Knowledge Base: docs.bwarm.com
- Video Tutorials: bwarm.com/tutorials

**Reporting Issues**:
1. Click user avatar → "Report Issue"
2. Describe the problem
3. Include screenshots if possible
4. Submit ticket

---

**Version**: 1.0.0
**Last Updated**: January 2024
**Support**: support@bwarm.com
