/**
 * SavedSearchManager Component
 *
 * Manages saved search queries with CRUD operations.
 * Features:
 * - List all saved searches with filtering
 * - Create new saved searches
 * - Update existing searches
 * - Delete searches (single and bulk)
 * - Mark as favorite
 * - View system presets
 * - Usage tracking
 * - Export/import functionality
 */

import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/api';
import type { SavedSearch, SavedSearchCreate, FilterConfig } from '../../types/savedSearch';
import AdvancedFilterBuilder from './AdvancedFilterBuilder';
import '../../styles/components/SavedSearchManager.css';

export interface SavedSearchManagerProps {
  onApplySearch?: (search: SavedSearch) => void;
  className?: string;
}

const AVAILABLE_FIELDS = [
  { value: 'title', label: 'Title', type: 'string' as const },
  { value: 'iswc', label: 'ISWC', type: 'string' as const },
  { value: 'has_iswc', label: 'Has ISWC', type: 'boolean' as const },
  { value: 'composers', label: 'Composers', type: 'string' as const },
  { value: 'publishers', label: 'Publishers', type: 'string' as const },
  { value: 'year', label: 'Year', type: 'number' as const },
  { value: 'duration', label: 'Duration', type: 'number' as const },
  { value: 'created_at', label: 'Created Date', type: 'date' as const },
];

const SavedSearchManager: React.FC<SavedSearchManagerProps> = ({ onApplySearch, className = '' }) => {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [presets, setPresets] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSearch, setEditingSearch] = useState<SavedSearch | null>(null);
  const [selectedSearchIds, setSelectedSearchIds] = useState<number[]>([]);
  const [filterFavorites, setFilterFavorites] = useState(false);
  const [showPresets, setShowPresets] = useState(true);

  // Form State
  const [searchName, setSearchName] = useState('');
  const [searchDescription, setSearchDescription] = useState('');
  const [filterConfig, setFilterConfig] = useState<FilterConfig>({ logic: 'AND', filters: [] });
  const [isFavorite, setIsFavorite] = useState(false);

  // Load searches and presets
  useEffect(() => {
    loadSearches();
    loadPresets();
  }, [filterFavorites]);

  const loadSearches = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getSavedSearches({
        include_presets: false,
        favorites_only: filterFavorites,
      });
      setSearches(response.searches);
    } catch (err: any) {
      setError(err.message || 'Failed to load saved searches');
    } finally {
      setLoading(false);
    }
  };

  const loadPresets = async () => {
    try {
      const presetsData = await apiClient.getSystemPresets();
      setPresets(presetsData);
    } catch (err: any) {
      console.error('Failed to load presets:', err);
    }
  };

  const handleCreateSearch = async () => {
    if (!searchName.trim()) {
      setError('Search name is required');
      return;
    }

    if (filterConfig.filters.length === 0) {
      setError('At least one filter is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const newSearch: SavedSearchCreate = {
        name: searchName.trim(),
        description: searchDescription.trim() || undefined,
        filter_config: filterConfig,
        is_favorite: isFavorite,
      };

      const created = await apiClient.createSavedSearch(newSearch);
      setSearches([created, ...searches]);
      resetForm();
      setShowCreateModal(false);
    } catch (err: any) {
      setError(err.message || 'Failed to create saved search');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSearch = async () => {
    if (!editingSearch) return;

    try {
      setLoading(true);
      setError(null);

      const updated = await apiClient.updateSavedSearch(editingSearch.id, {
        name: searchName.trim(),
        description: searchDescription.trim() || undefined,
        filter_config: filterConfig,
        is_favorite: isFavorite,
      });

      setSearches(searches.map((s) => (s.id === updated.id ? updated : s)));
      resetForm();
      setEditingSearch(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update saved search');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSearch = async (searchId: number) => {
    if (!confirm('Are you sure you want to delete this saved search?')) return;

    try {
      setLoading(true);
      await apiClient.deleteSavedSearchNew(searchId);
      setSearches(searches.filter((s) => s.id !== searchId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete saved search');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedSearchIds.length === 0) return;
    if (!confirm(`Delete ${selectedSearchIds.length} selected searches?`)) return;

    try {
      setLoading(true);
      await apiClient.bulkDeleteSearches(selectedSearchIds);
      setSearches(searches.filter((s) => !selectedSearchIds.includes(s.id)));
      setSelectedSearchIds([]);
    } catch (err: any) {
      setError(err.message || 'Failed to delete searches');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (search: SavedSearch) => {
    try {
      const updated = await apiClient.updateSavedSearch(search.id, {
        is_favorite: !search.is_favorite,
      });
      setSearches(searches.map((s) => (s.id === updated.id ? updated : s)));
    } catch (err: any) {
      setError(err.message || 'Failed to update favorite status');
    }
  };

  const handleApplySearch = async (search: SavedSearch) => {
    try {
      // Record usage
      await apiClient.recordSearchUse(search.id);

      // Update local state
      const updated = await apiClient.getSavedSearch(search.id);
      setSearches(searches.map((s) => (s.id === updated.id ? updated : s)));

      // Notify parent
      if (onApplySearch) {
        onApplySearch(updated);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to apply search');
    }
  };

  const handleEditSearch = (search: SavedSearch) => {
    setEditingSearch(search);
    setSearchName(search.name);
    setSearchDescription(search.description || '');
    setFilterConfig(search.filter_config);
    setIsFavorite(search.is_favorite);
  };

  const resetForm = () => {
    setSearchName('');
    setSearchDescription('');
    setFilterConfig({ logic: 'AND', filters: [] });
    setIsFavorite(false);
    setEditingSearch(null);
    setError(null);
  };

  const toggleSelectSearch = (searchId: number) => {
    setSelectedSearchIds((prev) =>
      prev.includes(searchId) ? prev.filter((id) => id !== searchId) : [...prev, searchId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedSearchIds.length === searches.length) {
      setSelectedSearchIds([]);
    } else {
      setSelectedSearchIds(searches.map((s) => s.id));
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className={`saved-search-manager ${className}`}>
      {/* Header */}
      <div className="manager-header">
        <div className="header-left">
          <h2>Saved Searches</h2>
          <button
            className={`filter-btn ${filterFavorites ? 'active' : ''}`}
            onClick={() => setFilterFavorites(!filterFavorites)}
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            Favorites Only
          </button>
          <button className="toggle-presets-btn" onClick={() => setShowPresets(!showPresets)}>
            {showPresets ? 'Hide' : 'Show'} Presets
          </button>
        </div>
        <div className="header-right">
          {selectedSearchIds.length > 0 && (
            <button className="bulk-delete-btn" onClick={handleBulkDelete}>
              Delete Selected ({selectedSearchIds.length})
            </button>
          )}
          <button className="create-btn" onClick={() => setShowCreateModal(true)}>
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                clipRule="evenodd"
              />
            </svg>
            New Search
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button onClick={() => setError(null)}>&times;</button>
        </div>
      )}

      {/* System Presets */}
      {showPresets && presets.length > 0 && (
        <div className="presets-section">
          <h3>System Presets</h3>
          <div className="searches-grid">
            {presets.map((preset) => (
              <div key={preset.id} className="search-card preset">
                <div className="card-header">
                  <div className="card-title">
                    <svg viewBox="0 0 20 20" fill="currentColor" className="preset-icon">
                      <path
                        fillRule="evenodd"
                        d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <h4>{preset.name}</h4>
                  </div>
                </div>
                {preset.description && <p className="card-description">{preset.description}</p>}
                <div className="card-footer">
                  <span className="filter-count">{preset.filter_config.filters.length} filters</span>
                  <button className="apply-btn" onClick={() => handleApplySearch(preset)}>
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Searches */}
      <div className="searches-section">
        <div className="section-header">
          <h3>My Searches</h3>
          {searches.length > 0 && (
            <label className="select-all">
              <input
                type="checkbox"
                checked={selectedSearchIds.length === searches.length}
                onChange={toggleSelectAll}
              />
              Select All
            </label>
          )}
        </div>

        {loading ? (
          <div className="loading-state">Loading...</div>
        ) : searches.length === 0 ? (
          <div className="empty-state">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clipRule="evenodd"
              />
            </svg>
            <h4>No saved searches</h4>
            <p>Create your first saved search to get started</p>
            <button className="create-btn" onClick={() => setShowCreateModal(true)}>
              Create Search
            </button>
          </div>
        ) : (
          <div className="searches-grid">
            {searches.map((search) => (
              <div
                key={search.id}
                className={`search-card ${selectedSearchIds.includes(search.id) ? 'selected' : ''}`}
              >
                <div className="card-header">
                  <input
                    type="checkbox"
                    checked={selectedSearchIds.includes(search.id)}
                    onChange={() => toggleSelectSearch(search.id)}
                  />
                  <div className="card-title">
                    <h4>{search.name}</h4>
                    <button
                      className={`favorite-btn ${search.is_favorite ? 'active' : ''}`}
                      onClick={() => handleToggleFavorite(search)}
                      title={search.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      <svg viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    </button>
                  </div>
                </div>

                {search.description && <p className="card-description">{search.description}</p>}

                <div className="card-meta">
                  <span className="filter-count">{search.filter_config.filters.length} filters</span>
                  <span className="logic-badge">{search.filter_config.logic}</span>
                  {search.last_used_at && (
                    <span className="last-used">Last used: {formatDate(search.last_used_at)}</span>
                  )}
                  <span className="use-count">{search.use_count} uses</span>
                </div>

                <div className="card-actions">
                  <button className="apply-btn" onClick={() => handleApplySearch(search)}>
                    Apply
                  </button>
                  <button className="edit-btn" onClick={() => handleEditSearch(search)}>
                    Edit
                  </button>
                  <button className="delete-btn" onClick={() => handleDeleteSearch(search.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingSearch) && (
        <div className="modal-overlay" onClick={() => (showCreateModal ? setShowCreateModal(false) : setEditingSearch(null))}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingSearch ? 'Edit Search' : 'Create New Search'}</h3>
              <button
                className="modal-close"
                onClick={() => (showCreateModal ? setShowCreateModal(false) : setEditingSearch(null))}
              >
                &times;
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Search Name *</label>
                <input
                  type="text"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  placeholder="e.g., Works without ISWC"
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={searchDescription}
                  onChange={(e) => setSearchDescription(e.target.value)}
                  placeholder="Optional description"
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={isFavorite}
                    onChange={(e) => setIsFavorite(e.target.checked)}
                  />
                  Mark as Favorite
                </label>
              </div>

              <div className="form-group">
                <label>Filters *</label>
                <AdvancedFilterBuilder
                  initialConfig={filterConfig}
                  onFilterChange={setFilterConfig}
                  availableFields={AVAILABLE_FIELDS}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="cancel-btn"
                onClick={() => (showCreateModal ? setShowCreateModal(false) : setEditingSearch(null))}
              >
                Cancel
              </button>
              <button
                className="save-btn"
                onClick={editingSearch ? handleUpdateSearch : handleCreateSearch}
                disabled={!searchName.trim() || filterConfig.filters.length === 0}
              >
                {editingSearch ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedSearchManager;
