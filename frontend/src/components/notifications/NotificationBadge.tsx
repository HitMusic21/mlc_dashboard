/**
 * NotificationBadge Component
 *
 * Displays a badge with unread notification count.
 * Features:
 * - Displays count up to 99 (shows "99+" for higher counts)
 * - Optional pulse animation for new notifications
 * - Color variants for different severity levels
 * - Accessible with aria-label
 * - Auto-hides when count is 0
 */

import React from 'react';
import '../../styles/components/NotificationBadge.css';

export interface NotificationBadgeProps {
  count: number;
  variant?: 'default' | 'error' | 'warning';
  pulse?: boolean;
  maxCount?: number;
  showZero?: boolean;
  className?: string;
  'aria-label'?: string;
}

const NotificationBadge: React.FC<NotificationBadgeProps> = ({
  count,
  variant = 'default',
  pulse = false,
  maxCount = 99,
  showZero = false,
  className = '',
  'aria-label': ariaLabel,
}) => {
  // Don't render if count is 0 and showZero is false
  if (count <= 0 && !showZero) {
    return null;
  }

  const displayCount = count > maxCount ? `${maxCount}+` : count.toString();

  const defaultAriaLabel = ariaLabel || `${count} unread notification${count === 1 ? '' : 's'}`;

  return (
    <span
      className={`notification-badge notification-badge--${variant} ${
        pulse ? 'notification-badge--pulse' : ''
      } ${className}`}
      aria-label={defaultAriaLabel}
      role="status"
    >
      {displayCount}
    </span>
  );
};

export default NotificationBadge;
