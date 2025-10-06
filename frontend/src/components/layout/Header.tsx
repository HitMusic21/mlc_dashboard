import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import type { UserResponse } from '../../types/api';
import { useNotificationsStore } from '../../stores/useNotificationsStore';
import { MobileNav } from './MobileNav';
import NotificationDropdown from '../notifications/NotificationDropdown';
import type { NotificationItem } from '../notifications/NotificationDropdown';
import PreferencesModal from '../preferences/PreferencesModal';
import DashboardLayoutEditor from '../preferences/DashboardLayoutEditor';

interface HeaderProps {
  user: UserResponse | null;
  onLogout: () => void;
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout, className = '' }) => {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false);
  const [isLayoutEditorOpen, setIsLayoutEditorOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const {
    notifications: allNotifications,
    unreadCount,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
  } = useNotificationsStore();

  // Fetch recent notifications on mount
  useEffect(() => {
    if (user) {
      fetchUnreadCount().catch(console.error);
      fetchNotifications({ limit: 5 }).catch(console.error);
    }
  }, [user, fetchUnreadCount, fetchNotifications]);

  // Convert to NotificationItem format for dropdown
  const notifications: NotificationItem[] = allNotifications.slice(0, 5).map((n) => ({
    id: n.id,
    type: n.type,
    severity: n.severity,
    title: n.title,
    message: n.message,
    is_read: n.is_read,
    created_at: n.created_at,
    action_url: n.action_url,
  }));

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isDropdownOpen]);

  // Notification handlers
  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead(notificationId);
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsRead();
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  const handleViewAllNotifications = () => {
    navigate('/notifications');
  };

  return (
    <header className={`app-header ${className}`}>
      <div className="header-content">
        {/* Mobile Navigation Toggle */}
        <MobileNav
          isOpen={isMobileNavOpen}
          onToggle={() => setIsMobileNavOpen(!isMobileNavOpen)}
          user={user}
        />

        {/* Logo and title */}
        <div className="header-brand">
          <svg
            className="brand-logo"
            width="32"
            height="32"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M16 2L4 8v8c0 7.5 5 14.5 12 18 7-3.5 12-10.5 12-18V8L16 2z"
              fill="currentColor"
              opacity="0.2"
            />
            <path
              d="M16 2L4 8v8c0 7.5 5 14.5 12 18 7-3.5 12-10.5 12-18V8L16 2z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M12 16l3 3 6-6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <h1 className="brand-title">BWARM Dashboard</h1>
        </div>

        {/* Navigation links */}
        <nav className="header-nav" aria-label="Main navigation">
          <NavLink to="/" className="nav-link" end>
            Dashboard
          </NavLink>
          <NavLink to="/works" className="nav-link">
            Browse Works
          </NavLink>
          <NavLink to="/catalog" className="nav-link">
            Catalog Matcher
          </NavLink>
          <NavLink to="/saved-searches" className="nav-link">
            Saved Searches
          </NavLink>
          {user?.role === 'admin' && (
            <NavLink to="/admin" className="nav-link">
              Admin
            </NavLink>
          )}
        </nav>

        {/* Notifications */}
        {user && (
          <NotificationDropdown
            notifications={notifications}
            unreadCount={unreadCount}
            onMarkAsRead={handleMarkAsRead}
            onMarkAllAsRead={handleMarkAllAsRead}
            onViewAll={handleViewAllNotifications}
          />
        )}

        {/* User menu */}
        {user && (
          <div className="header-user" ref={dropdownRef}>
            <button
              type="button"
              className="user-button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              aria-haspopup="true"
              aria-expanded={isDropdownOpen}
            >
              <div className="user-avatar">
                {user.full_name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="user-info">
                <span className="user-name">{user.full_name || user.email}</span>
                <span className="user-role">{user.role}</span>
              </div>
              <svg
                className={`dropdown-icon ${isDropdownOpen ? 'open' : ''}`}
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M4 6l4 4 4-4"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>

            {isDropdownOpen && (
              <div className="user-dropdown" role="menu">
                <div className="dropdown-section">
                  <div className="dropdown-header">
                    <p className="dropdown-email">{user.email}</p>
                  </div>
                </div>

                <div className="dropdown-divider" />

                <div className="dropdown-section">
                  <button
                    type="button"
                    className="dropdown-item"
                    onClick={() => {
                      setIsDropdownOpen(false);
                      setIsPreferencesOpen(true);
                    }}
                    role="menuitem"
                  >
                    <svg
                      className="dropdown-icon"
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      aria-hidden="true"
                    >
                      <path
                        d="M8 10a2 2 0 100-4 2 2 0 000 4z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M13.45 8.83l1.38-1.01c.2-.15.27-.42.15-.65l-1.3-2.25a.5.5 0 00-.61-.22l-1.62.54a5.5 5.5 0 00-1.73-1l-.36-1.7a.5.5 0 00-.49-.41H6.13a.5.5 0 00-.49.41l-.36 1.7a5.5 5.5 0 00-1.73 1l-1.62-.54a.5.5 0 00-.61.22L.02 7.17a.5.5 0 00.15.65L1.55 8.83a5.27 5.27 0 000 2l-1.38 1.01a.5.5 0 00-.15.65l1.3 2.25a.5.5 0 00.61.22l1.62-.54a5.5 5.5 0 001.73 1l.36 1.7a.5.5 0 00.49.41h2.74a.5.5 0 00.49-.41l.36-1.7a5.5 5.5 0 001.73-1l1.62.54a.5.5 0 00.61-.22l1.3-2.25a.5.5 0 00-.15-.65L13.45 10.83a5.27 5.27 0 000-2z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>Preferences</span>
                  </button>

                  <button
                    type="button"
                    className="dropdown-item"
                    onClick={() => {
                      setIsDropdownOpen(false);
                      setIsLayoutEditorOpen(true);
                    }}
                    role="menuitem"
                  >
                    <svg
                      className="dropdown-icon"
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      aria-hidden="true"
                    >
                      <path
                        d="M2 2h5v5H2V2zm7 0h5v5H9V2zM2 9h5v5H2V9zm7 0h5v5H9V9z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>Dashboard Layout</span>
                  </button>
                </div>

                <div className="dropdown-divider" />

                <div className="dropdown-section">
                  <button
                    type="button"
                    className="dropdown-item"
                    onClick={() => {
                      setIsDropdownOpen(false);
                      onLogout();
                    }}
                    role="menuitem"
                  >
                    <svg
                      className="dropdown-icon"
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      aria-hidden="true"
                    >
                      <path
                        d="M6 14H3a1 1 0 01-1-1V3a1 1 0 011-1h3M11 11l3-3-3-3M14 8H6"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      <PreferencesModal
        isOpen={isPreferencesOpen}
        onClose={() => setIsPreferencesOpen(false)}
      />
      <DashboardLayoutEditor
        isOpen={isLayoutEditorOpen}
        onClose={() => setIsLayoutEditorOpen(false)}
      />
    </header>
  );
};
