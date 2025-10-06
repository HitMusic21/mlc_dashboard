/**
 * Saved Searches Page
 *
 * Dedicated page for managing saved search configurations.
 * Users can create, view, edit, and delete saved searches,
 * and apply them to filter works.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import SavedSearchManager from '../components/search/SavedSearchManager';
import type { SavedSearch } from '../types/savedSearch';

const SavedSearches: React.FC = () => {
  const navigate = useNavigate();

  const handleApplySearch = (search: SavedSearch) => {
    // Navigate to Works Browser with the search applied
    navigate('/works', {
      state: { appliedSearch: search }
    });
  };

  return (
    <div className="saved-searches-page">
      <SavedSearchManager onApplySearch={handleApplySearch} />
    </div>
  );
};

export default SavedSearches;
