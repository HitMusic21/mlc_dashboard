import React, { useState } from 'react';

export interface FilterConfig {
  has_iswc?: boolean;
  has_disputed_rights?: boolean;
  created_after?: string;
  created_before?: string;
  [key: string]: any;
}

interface FilterPanelProps {
  filters: FilterConfig;
  onFilterChange: (filters: FilterConfig) => void;
  onApply?: () => void;
  onReset?: () => void;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  className?: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFilterChange,
  onApply,
  onReset,
  collapsible = true,
  defaultExpanded = true,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [localFilters, setLocalFilters] = useState<FilterConfig>(filters);

  const handleCheckboxChange = (key: keyof FilterConfig, checked: boolean) => {
    const newFilters = { ...localFilters, [key]: checked };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleDateChange = (key: keyof FilterConfig, value: string) => {
    const newFilters = { ...localFilters, [key]: value || undefined };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleApply = () => {
    onApply?.();
  };

  const handleReset = () => {
    const resetFilters: FilterConfig = {
      has_iswc: undefined,
      has_disputed_rights: undefined,
      created_after: undefined,
      created_before: undefined,
    };
    setLocalFilters(resetFilters);
    onFilterChange(resetFilters);
    onReset?.();
  };

  const hasActiveFilters = Object.values(localFilters).some(
    (value) => value !== undefined && value !== null && value !== ''
  );

  return (
    <div className={`filter-panel ${className}`}>
      {collapsible && (
        <button
          className="filter-panel-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          aria-controls="filter-panel-content"
        >
          <span className="filter-panel-title">
            Filters
            {hasActiveFilters && <span className="active-indicator"> (Active)</span>}
          </span>
          <svg
            className={`toggle-icon ${isExpanded ? 'expanded' : ''}`}
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
      )}

      {(!collapsible || isExpanded) && (
        <div id="filter-panel-content" className="filter-panel-content">
          {/* Boolean filters */}
          <div className="filter-section">
            <h3 className="filter-section-title">Work Properties</h3>

            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={localFilters.has_iswc === true}
                onChange={(e) => handleCheckboxChange('has_iswc', e.target.checked)}
              />
              <span>Has ISWC</span>
            </label>

            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={localFilters.has_disputed_rights === true}
                onChange={(e) => handleCheckboxChange('has_disputed_rights', e.target.checked)}
              />
              <span>Has Disputed Rights</span>
            </label>
          </div>

          {/* Date range filters */}
          <div className="filter-section">
            <h3 className="filter-section-title">Date Range</h3>

            <div className="filter-date-group">
              <label className="filter-label">
                <span className="label-text">Created After</span>
                <input
                  type="date"
                  value={localFilters.created_after || ''}
                  onChange={(e) => handleDateChange('created_after', e.target.value)}
                  className="filter-date-input"
                />
              </label>

              <label className="filter-label">
                <span className="label-text">Created Before</span>
                <input
                  type="date"
                  value={localFilters.created_before || ''}
                  onChange={(e) => handleDateChange('created_before', e.target.value)}
                  className="filter-date-input"
                />
              </label>
            </div>
          </div>

          {/* Action buttons */}
          <div className="filter-actions">
            <button
              type="button"
              onClick={handleApply}
              className="filter-button apply-button"
              disabled={!hasActiveFilters}
            >
              Apply Filters
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="filter-button reset-button"
              disabled={!hasActiveFilters}
            >
              Reset
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
