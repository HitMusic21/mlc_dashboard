/**
 * Notifications Store
 *
 * Zustand store for managing notifications state.
 * Handles fetching, marking as read, and deleting notifications.
 */

import { create } from 'zustand';
import { apiClient } from '../services/api';
import type { Notification, NotificationListResponse } from '../types/notifications';

interface NotificationsState {
  // State
  notifications: Notification[];
  unreadCount: number;
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchNotifications: (params?: { is_read?: boolean; page?: number; limit?: number }) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (notificationId: string) => Promise<void>;
  clearReadNotifications: () => Promise<void>;
  reset: () => void;
}

export const useNotificationsStore = create<NotificationsState>((set) => ({
  // Initial state
  notifications: [],
  unreadCount: 0,
  total: 0,
  page: 1,
  limit: 20,
  hasMore: false,
  isLoading: false,
  error: null,

  // Fetch notifications
  fetchNotifications: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response: NotificationListResponse = await apiClient.getNotifications(params);
      set({
        notifications: response.notifications,
        total: response.total,
        page: response.page,
        limit: response.limit,
        hasMore: response.has_more,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch notifications';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  // Fetch unread count
  fetchUnreadCount: async () => {
    try {
      const response = await apiClient.getUnreadCount();
      set({ unreadCount: response.unread_count });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch unread count';
      set({ error: errorMessage });
      throw error;
    }
  },

  // Mark notification as read
  markAsRead: async (notificationId: string) => {
    try {
      const updatedNotification = await apiClient.markNotificationAsRead(notificationId);

      // Update local state
      set((state) => ({
        notifications: state.notifications.map((n) =>
          n.id === notificationId ? updatedNotification : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to mark as read';
      set({ error: errorMessage });
      throw error;
    }
  },

  // Mark all notifications as read
  markAllAsRead: async () => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.markAllNotificationsAsRead();

      // Update local state
      set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
        unreadCount: 0,
        isLoading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to mark all as read';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  // Delete notification
  deleteNotification: async (notificationId: string) => {
    try {
      await apiClient.deleteNotification(notificationId);

      // Update local state
      set((state) => {
        const notification = state.notifications.find((n) => n.id === notificationId);
        const wasUnread = notification && !notification.is_read;

        return {
          notifications: state.notifications.filter((n) => n.id !== notificationId),
          total: Math.max(0, state.total - 1),
          unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
        };
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete notification';
      set({ error: errorMessage });
      throw error;
    }
  },

  // Clear all read notifications
  clearReadNotifications: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.clearReadNotifications();

      // Update local state - remove all read notifications
      set((state) => ({
        notifications: state.notifications.filter((n) => !n.is_read),
        total: Math.max(0, state.total - response.deleted_count),
        isLoading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to clear notifications';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  // Reset state
  reset: () => {
    set({
      notifications: [],
      unreadCount: 0,
      total: 0,
      page: 1,
      limit: 20,
      hasMore: false,
      isLoading: false,
      error: null,
    });
  },
}));

// Selectors
export const selectUnreadNotifications = (state: NotificationsState) =>
  state.notifications.filter((n) => !n.is_read);

export const selectReadNotifications = (state: NotificationsState) =>
  state.notifications.filter((n) => n.is_read);

export const selectRecentNotifications = (state: NotificationsState, limit: number = 5) =>
  state.notifications.slice(0, limit);
