/**
 * SavedSearchPanel Component
 *
 * Displays and manages user's saved search queries.
 * Features:
 * - List of saved searches with apply/delete actions
 * - Quick apply search filters
 * - Delete saved searches with confirmation
 * - Empty state with call-to-action
 * - Loading state
 * - Search filter display (shows active filters)
 */

import React, { useState } from 'react';
import '../../styles/components/SavedSearchPanel.css';

export interface SavedSearch {
  id: string;
  name: string;
  filters: Record<string, unknown>;
  created_at: string;
}

export interface SavedSearchPanelProps {
  searches: SavedSearch[];
  onApply: (search: SavedSearch) => void;
  onDelete: (searchId: string) => void;
  onCreate?: () => void;
  loading?: boolean;
  className?: string;
}

const SavedSearchPanel: React.FC<SavedSearchPanelProps> = ({
  searches,
  onApply,
  onDelete,
  onCreate,
  loading = false,
  className = '',
}) => {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = (searchId: string) => {
    if (deletingId === searchId) {
      // Confirm deletion
      onDelete(searchId);
      setDeletingId(null);
    } else {
      // Show confirmation
      setDeletingId(searchId);
      // Auto-cancel after 3 seconds
      setTimeout(() => {
        setDeletingId((current) => (current === searchId ? null : current));
      }, 3000);
    }
  };

  const getFilterCount = (filters: Record<string, unknown>): number => {
    return Object.keys(filters).filter((key) => {
      const value = filters[key];
      return value !== null && value !== undefined && value !== '';
    }).length;
  };

  const getFilterSummary = (filters: Record<string, unknown>): string => {
    const filterEntries = Object.entries(filters).filter(
      ([, value]) => value !== null && value !== undefined && value !== ''
    );

    if (filterEntries.length === 0) return 'No filters';
    if (filterEntries.length === 1) {
      const [key, value] = filterEntries[0];
      return `${key}: ${String(value)}`;
    }

    return `${filterEntries.length} filters applied`;
  };

  const renderLoadingState = () => (
    <div className="saved-search-panel__loading">
      {[...Array(3)].map((_, index) => (
        <div key={index} className="saved-search-panel__item saved-search-panel__item--loading">
          <div className="saved-search-panel__item-header">
            <div className="skeleton saved-search-panel__name-skeleton" />
            <div className="skeleton saved-search-panel__actions-skeleton" />
          </div>
          <div className="skeleton saved-search-panel__filters-skeleton" />
        </div>
      ))}
    </div>
  );

  const renderEmptyState = () => (
    <div className="saved-search-panel__empty">
      <svg
        className="saved-search-panel__empty-icon"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
          clipRule="evenodd"
        />
      </svg>
      <p className="saved-search-panel__empty-message">No saved searches</p>
      {onCreate && (
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={onCreate}
        >
          Create first search
        </button>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className={`saved-search-panel ${className}`}>
        <h3 className="saved-search-panel__title">Saved Searches</h3>
        <div className="saved-search-panel__list">{renderLoadingState()}</div>
      </div>
    );
  }

  if (searches.length === 0) {
    return (
      <div className={`saved-search-panel ${className}`}>
        <h3 className="saved-search-panel__title">Saved Searches</h3>
        {renderEmptyState()}
      </div>
    );
  }

  return (
    <div className={`saved-search-panel ${className}`}>
      <div className="saved-search-panel__header">
        <h3 className="saved-search-panel__title">Saved Searches</h3>
        {onCreate && (
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={onCreate}
          >
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path
                fillRule="evenodd"
                d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                clipRule="evenodd"
              />
            </svg>
            New
          </button>
        )}
      </div>

      <div className="saved-search-panel__list">
        {searches.map((search) => (
          <div
            key={search.id}
            className={`saved-search-panel__item ${
              deletingId === search.id ? 'saved-search-panel__item--deleting' : ''
            }`}
          >
            <div className="saved-search-panel__item-header">
              <div className="saved-search-panel__item-info">
                <h4 className="saved-search-panel__item-name">{search.name}</h4>
                <span className="saved-search-panel__item-count">
                  {getFilterCount(search.filters)} filter
                  {getFilterCount(search.filters) !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="saved-search-panel__item-actions">
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => onApply(search)}
                  title="Apply this search"
                >
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>

                <button
                  type="button"
                  className={`btn btn-ghost btn-sm ${
                    deletingId === search.id ? 'btn-danger' : ''
                  }`}
                  onClick={() => handleDelete(search.id)}
                  title={deletingId === search.id ? 'Click again to confirm' : 'Delete'}
                >
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <p className="saved-search-panel__item-filters">
              {getFilterSummary(search.filters)}
            </p>

            {deletingId === search.id && (
              <div className="saved-search-panel__delete-confirm">
                Click delete again to confirm
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SavedSearchPanel;
