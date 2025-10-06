/**
 * Notifications Types
 *
 * Type definitions for user notifications system.
 */

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface Notification {
  id: string;
  user_id: number;
  type: NotificationType;
  severity: NotificationSeverity;
  title: string;
  message: string;
  is_read: boolean;
  related_entity_type?: string;
  related_entity_id?: string;
  action_url?: string;
  expires_at?: string;
  created_at: string;
  read_at?: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAllReadResponse {
  marked_count: number;
}
