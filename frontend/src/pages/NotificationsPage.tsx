/**
 * NotificationsPage Component
 *
 * Full page for managing all user notifications.
 * Features:
 * - All/Unread tabs
 * - Mark as read/unread
 * - Delete notifications
 * - Clear all read notifications
 * - Pagination
 * - Empty states
 */

import React, { useState, useEffect } from 'react';
import { useNotificationsStore } from '../stores/useNotificationsStore';
import { usePreferencesStore, selectItemsPerPage } from '../stores/usePreferencesStore';
import type { Notification } from '../types/notifications';
import '../styles/pages/NotificationsPage.css';

type TabType = 'all' | 'unread';

export const NotificationsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const limit = usePreferencesStore(selectItemsPerPage);

  const {
    notifications,
    unreadCount,
    isLoading,
    error,
    fetchNotifications,
    markAsRead,
    deleteNotification,
    clearReadNotifications,
  } = useNotificationsStore();

  // Fetch notifications on mount and tab change
  useEffect(() => {
    const params = activeTab === 'unread' ? { is_read: false, limit } : { limit };
    fetchNotifications(params).catch((err) => {
      console.error('Failed to fetch notifications:', err);
    });
  }, [activeTab, limit, fetchNotifications]);

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead(notificationId);
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const handleDelete = async (notificationId: string) => {
    try {
      await deleteNotification(notificationId);
    } catch (err) {
      console.error('Failed to delete notification:', err);
    }
  };

  const handleClearRead = async () => {
    if (window.confirm('Are you sure you want to delete all read notifications?')) {
      try {
        await clearReadNotifications();
      } catch (err) {
        console.error('Failed to clear notifications:', err);
      }
    }
  };

  const toggleExpanded = (notificationId: string) => {
    setExpandedId(expandedId === notificationId ? null : notificationId);
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'error':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'warning':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
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
          <svg viewBox="0 0 20 20" fill="currentColor" width="24" height="24">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins === 1 ? '' : 's'} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;

    return date.toLocaleDateString();
  };

  const filteredNotifications =
    activeTab === 'unread' ? notifications.filter((n) => !n.is_read) : notifications;

  return (
    <div className="notifications-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="page-description">
            {unreadCount > 0
              ? `You have ${unreadCount} unread notification${unreadCount === 1 ? '' : 's'}`
              : 'All caught up!'}
          </p>
        </div>

        {notifications.some((n) => n.is_read) && (
          <button type="button" className="btn btn-secondary" onClick={handleClearRead}>
            Clear Read
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="notifications-tabs">
        <button
          type="button"
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All
          {notifications.length > 0 && <span className="tab-count">{notifications.length}</span>}
        </button>
        <button
          type="button"
          className={`tab ${activeTab === 'unread' ? 'active' : ''}`}
          onClick={() => setActiveTab('unread')}
        >
          Unread
          {unreadCount > 0 && <span className="tab-count">{unreadCount}</span>}
        </button>
      </div>

      {/* Content */}
      <div className="notifications-content">
        {error && (
          <div className="alert alert-error">
            <p>{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="notifications-loading">
            <div className="spinner" />
            <p>Loading notifications...</p>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="notifications-empty">
            <svg viewBox="0 0 20 20" fill="currentColor" width="48" height="48" className="empty-icon">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
            </svg>
            <h3 className="empty-title">
              {activeTab === 'unread' ? 'No unread notifications' : 'No notifications'}
            </h3>
            <p className="empty-message">
              {activeTab === 'unread'
                ? "You're all caught up! Check back later for updates."
                : "You don't have any notifications yet."}
            </p>
          </div>
        ) : (
          <div className="notifications-list">
            {filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`notification-item ${notification.is_read ? 'read' : 'unread'} ${
                  expandedId === notification.id ? 'expanded' : ''
                } notification-${notification.type}`}
              >
                <div className="notification-header" onClick={() => toggleExpanded(notification.id)}>
                  <div className="notification-icon">{getNotificationIcon(notification.type)}</div>

                  <div className="notification-info">
                    <div className="notification-title-row">
                      <h4 className="notification-title">{notification.title}</h4>
                      {!notification.is_read && <span className="unread-dot" />}
                    </div>
                    <p className="notification-message">{notification.message}</p>
                    <span className="notification-time">{formatDate(notification.created_at)}</span>
                  </div>

                  <div className="notification-actions">
                    {!notification.is_read && (
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMarkAsRead(notification.id);
                        }}
                        title="Mark as read"
                      >
                        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                    )}
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm text-error"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(notification.id);
                      }}
                      title="Delete"
                    >
                      <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                        <path
                          fillRule="evenodd"
                          d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>
                  </div>
                </div>

                {expandedId === notification.id && notification.action_url && (
                  <div className="notification-details">
                    <a href={notification.action_url} className="btn btn-primary btn-sm">
                      View Details
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
