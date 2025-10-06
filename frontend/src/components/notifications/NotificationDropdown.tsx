/**
 * NotificationDropdown Component
 *
 * Dropdown menu for displaying recent notifications in the header.
 * Features:
 * - Bell icon trigger with unread count badge
 * - Recent notifications list (max 5)
 * - Mark individual notifications as read
 * - Mark all as read action
 * - View all notifications link
 * - Empty state
 * - Click outside to close
 * - Keyboard navigation support
 */

import React, { useEffect, useRef, useState } from 'react';
import NotificationBadge from './NotificationBadge';
import '../../styles/components/NotificationDropdown.css';

export interface NotificationItem {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  action_url?: string;
}

export interface NotificationDropdownProps {
  notifications: NotificationItem[];
  unreadCount: number;
  onMarkAsRead: (notificationId: string) => void;
  onMarkAllAsRead: () => void;
  onViewAll: () => void;
  loading?: boolean;
  className?: string;
}

const NotificationDropdown: React.FC<NotificationDropdownProps> = ({
  notifications,
  unreadCount,
  onMarkAsRead,
  onMarkAllAsRead,
  onViewAll,
  loading = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Close dropdown on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  const getNotificationIcon = (type: NotificationItem['type']): React.ReactNode => {
    switch (type) {
      case 'success':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'error':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'warning':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'info':
      default:
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  const getRelativeTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 1000 / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffMin < 1) return 'just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHour < 24) return `${diffHour}h ago`;
    if (diffDay < 7) return `${diffDay}d ago`;

    return date.toLocaleDateString();
  };

  const handleNotificationClick = (notification: NotificationItem) => {
    if (!notification.is_read) {
      onMarkAsRead(notification.id);
    }
    if (notification.action_url) {
      window.location.href = notification.action_url;
    }
  };

  return (
    <div className={`notification-dropdown ${className}`}>
      <button
        ref={buttonRef}
        type="button"
        className="notification-dropdown__trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label={`Notifications. ${unreadCount} unread`}
      >
        <svg
          className="notification-dropdown__bell-icon"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
        </svg>
        {unreadCount > 0 && <NotificationBadge count={unreadCount} pulse />}
      </button>

      {isOpen && (
        <div
          ref={dropdownRef}
          className="notification-dropdown__menu"
          role="menu"
        >
          <div className="notification-dropdown__header">
            <h3 className="notification-dropdown__title">Notifications</h3>
            {unreadCount > 0 && (
              <button
                type="button"
                className="notification-dropdown__mark-all-read"
                onClick={onMarkAllAsRead}
              >
                Mark all as read
              </button>
            )}
          </div>

          <div className="notification-dropdown__list">
            {loading ? (
              <div className="notification-dropdown__loading">
                <div className="spinner" />
                <p>Loading notifications...</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="notification-dropdown__empty">
                <svg className="notification-dropdown__empty-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
                </svg>
                <p>No notifications</p>
              </div>
            ) : (
              notifications.slice(0, 5).map((notification) => (
                <button
                  key={notification.id}
                  type="button"
                  className={`notification-dropdown__item ${
                    !notification.is_read ? 'notification-dropdown__item--unread' : ''
                  } notification-dropdown__item--${notification.type}`}
                  onClick={() => handleNotificationClick(notification)}
                  role="menuitem"
                >
                  <div className="notification-dropdown__item-icon">
                    {getNotificationIcon(notification.type)}
                  </div>

                  <div className="notification-dropdown__item-content">
                    <div className="notification-dropdown__item-header">
                      <h4 className="notification-dropdown__item-title">
                        {notification.title}
                      </h4>
                      <time className="notification-dropdown__item-time">
                        {getRelativeTime(notification.created_at)}
                      </time>
                    </div>
                    <p className="notification-dropdown__item-message">
                      {notification.message}
                    </p>
                  </div>

                  {!notification.is_read && (
                    <div className="notification-dropdown__item-indicator" />
                  )}
                </button>
              ))
            )}
          </div>

          {notifications.length > 0 && (
            <div className="notification-dropdown__footer">
              <button
                type="button"
                className="notification-dropdown__view-all"
                onClick={() => {
                  onViewAll();
                  setIsOpen(false);
                }}
              >
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;
