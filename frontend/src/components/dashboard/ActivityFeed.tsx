/**
 * ActivityFeed Component
 *
 * Displays a feed of recent activity logs with user actions and timestamps.
 * Features:
 * - Activity list with icons based on action type
 * - Relative timestamp formatting (e.g., "2 hours ago")
 * - User information display
 * - Status indicators (success, failure, pending)
 * - Load more pagination
 * - Loading and empty states
 */

import React from 'react';
import '../../styles/components/ActivityFeed.css';

export interface ActivityItem {
  id: string;
  user_id?: number;
  user_email?: string;
  action: string;
  description: string;
  status: 'success' | 'failure' | 'pending';
  created_at: string;
  log_metadata?: Record<string, unknown>;
}

export interface ActivityFeedProps {
  activities: ActivityItem[];
  loading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  emptyMessage?: string;
  className?: string;
  maxItems?: number;
}

const ActivityFeed: React.FC<ActivityFeedProps> = ({
  activities,
  loading = false,
  hasMore = false,
  onLoadMore,
  emptyMessage = 'No recent activity',
  className = '',
  maxItems,
}) => {
  const displayActivities = maxItems ? activities.slice(0, maxItems) : activities;

  const getRelativeTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffSec < 60) return 'just now';
    if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
  };

  const getActionIcon = (action: string): React.ReactNode => {
    const [entity] = action.split('.');

    switch (entity) {
      case 'catalog':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>
        );
      case 'work':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'user':
      case 'auth':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'preferences':
        return (
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
              clipRule="evenodd"
            />
          </svg>
        );
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

  const renderLoadingState = () => (
    <div className="activity-feed__loading">
      {[...Array(3)].map((_, index) => (
        <div key={index} className="activity-feed__item activity-feed__item--loading">
          <div className="skeleton activity-feed__icon-skeleton" />
          <div className="activity-feed__item-content">
            <div className="skeleton activity-feed__description-skeleton" />
            <div className="skeleton activity-feed__timestamp-skeleton" />
          </div>
        </div>
      ))}
    </div>
  );

  const renderEmptyState = () => (
    <div className="activity-feed__empty">
      <svg className="activity-feed__empty-icon" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z"
          clipRule="evenodd"
        />
      </svg>
      <p className="activity-feed__empty-message">{emptyMessage}</p>
    </div>
  );

  if (loading && activities.length === 0) {
    return (
      <div className={`activity-feed ${className}`}>
        <h3 className="activity-feed__title">Recent Activity</h3>
        <div className="activity-feed__list">{renderLoadingState()}</div>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className={`activity-feed ${className}`}>
        <h3 className="activity-feed__title">Recent Activity</h3>
        {renderEmptyState()}
      </div>
    );
  }

  return (
    <div className={`activity-feed ${className}`}>
      <h3 className="activity-feed__title">Recent Activity</h3>

      <div className="activity-feed__list">
        {displayActivities.map((activity) => (
          <div
            key={activity.id}
            className={`activity-feed__item activity-feed__item--${activity.status}`}
          >
            <div className="activity-feed__icon">{getActionIcon(activity.action)}</div>

            <div className="activity-feed__item-content">
              <div className="activity-feed__description">
                {activity.user_email && (
                  <span className="activity-feed__user">{activity.user_email}</span>
                )}
                <span className="activity-feed__action">{activity.description}</span>
              </div>

              <div className="activity-feed__meta">
                <time
                  className="activity-feed__timestamp"
                  dateTime={activity.created_at}
                  title={new Date(activity.created_at).toLocaleString()}
                >
                  {getRelativeTime(activity.created_at)}
                </time>

                {activity.status === 'failure' && (
                  <span className="activity-feed__status activity-feed__status--failure">
                    Failed
                  </span>
                )}
                {activity.status === 'pending' && (
                  <span className="activity-feed__status activity-feed__status--pending">
                    Pending
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {hasMore && onLoadMore && (
        <button
          type="button"
          className="activity-feed__load-more btn btn-ghost"
          onClick={onLoadMore}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
};

export default ActivityFeed;
