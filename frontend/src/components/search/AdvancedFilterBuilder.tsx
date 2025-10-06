/**
 * AdvancedFilterBuilder Component
 *
 * Allows users to build complex filter queries with AND/OR logic.
 * Features:
 * - Multiple filter conditions
 * - Field selection (title, composer, iswc, etc.)
 * - Operator selection (equals, contains, greater_than, etc.)
 * - Value input with type-appropriate controls
 * - AND/OR logic toggle
 * - Add/remove filter conditions
 * - Real-time validation
 * - Sort configuration
 */

import React, { useState } from 'react';
import type { FilterConfig, FilterCondition, FilterOperator } from '../../types/savedSearch';
import '../../styles/components/AdvancedFilterBuilder.css';

export interface AdvancedFilterBuilderProps {
  initialConfig?: FilterConfig;
  onFilterChange: (config: FilterConfig) => void;
  availableFields: Array<{ value: string; label: string; type: 'string' | 'number' | 'boolean' | 'date' }>;
  className?: string;
}

const OPERATORS: Array<{ value: FilterOperator; label: string; types: Array<'string' | 'number' | 'boolean' | 'date'> }> = [
  { value: 'equals', label: 'Equals', types: ['string', 'number', 'boolean'] },
  { value: 'not_equals', label: 'Not Equals', types: ['string', 'number', 'boolean'] },
  { value: 'contains', label: 'Contains', types: ['string'] },
  { value: 'not_contains', label: 'Does Not Contain', types: ['string'] },
  { value: 'starts_with', label: 'Starts With', types: ['string'] },
  { value: 'ends_with', label: 'Ends With', types: ['string'] },
  { value: 'greater_than', label: 'Greater Than', types: ['number', 'date'] },
  { value: 'less_than', label: 'Less Than', types: ['number', 'date'] },
  { value: 'greater_than_or_equal', label: 'Greater Than or Equal', types: ['number', 'date'] },
  { value: 'less_than_or_equal', label: 'Less Than or Equal', types: ['number', 'date'] },
  { value: 'in', label: 'In List', types: ['string', 'number'] },
  { value: 'not_in', label: 'Not In List', types: ['string', 'number'] },
  { value: 'is_null', label: 'Is Empty', types: ['string', 'number', 'boolean', 'date'] },
  { value: 'is_not_null', label: 'Is Not Empty', types: ['string', 'number', 'boolean', 'date'] },
];

const AdvancedFilterBuilder: React.FC<AdvancedFilterBuilderProps> = ({
  initialConfig,
  onFilterChange,
  availableFields,
  className = '',
}) => {
  const [config, setConfig] = useState<FilterConfig>(
    initialConfig || {
      logic: 'AND',
      filters: [],
    }
  );

  const updateConfig = (newConfig: FilterConfig) => {
    setConfig(newConfig);
    onFilterChange(newConfig);
  };

  const addFilter = () => {
    const newFilter: FilterCondition = {
      field: availableFields[0]?.value || '',
      operator: 'equals',
      value: '',
    };

    updateConfig({
      ...config,
      filters: [...config.filters, newFilter],
    });
  };

  const removeFilter = (index: number) => {
    updateConfig({
      ...config,
      filters: config.filters.filter((_, i) => i !== index),
    });
  };

  const updateFilter = (index: number, updates: Partial<FilterCondition>) => {
    const newFilters = [...config.filters];
    newFilters[index] = { ...newFilters[index], ...updates };

    updateConfig({
      ...config,
      filters: newFilters,
    });
  };

  const toggleLogic = () => {
    updateConfig({
      ...config,
      logic: config.logic === 'AND' ? 'OR' : 'AND',
    });
  };

  const updateSort = (field: string, order: 'asc' | 'desc') => {
    updateConfig({
      ...config,
      sort: { field, order },
    });
  };

  const clearSort = () => {
    const { sort, ...rest } = config;
    updateConfig(rest as FilterConfig);
  };

  const getFieldType = (fieldValue: string): 'string' | 'number' | 'boolean' | 'date' => {
    return availableFields.find((f) => f.value === fieldValue)?.type || 'string';
  };

  const getAvailableOperators = (fieldValue: string) => {
    const fieldType = getFieldType(fieldValue);
    return OPERATORS.filter((op) => op.types.includes(fieldType));
  };

  const renderValueInput = (filter: FilterCondition, index: number) => {
    const fieldType = getFieldType(filter.field);

    // Operators that don't need a value
    if (filter.operator === 'is_null' || filter.operator === 'is_not_null') {
      return null;
    }

    // List operators (in, not_in)
    if (filter.operator === 'in' || filter.operator === 'not_in') {
      return (
        <input
          type="text"
          className="filter-value-input"
          placeholder="Comma-separated values"
          value={Array.isArray(filter.value) ? filter.value.join(', ') : filter.value}
          onChange={(e) => {
            const values = e.target.value.split(',').map((v) => v.trim());
            updateFilter(index, { value: values });
          }}
        />
      );
    }

    // Boolean field
    if (fieldType === 'boolean') {
      return (
        <select
          className="filter-value-select"
          value={filter.value?.toString() || ''}
          onChange={(e) => updateFilter(index, { value: e.target.value === 'true' })}
        >
          <option value="">Select...</option>
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      );
    }

    // Number field
    if (fieldType === 'number') {
      return (
        <input
          type="number"
          className="filter-value-input"
          placeholder="Enter number"
          value={filter.value || ''}
          onChange={(e) => updateFilter(index, { value: parseFloat(e.target.value) || '' })}
        />
      );
    }

    // Date field
    if (fieldType === 'date') {
      return (
        <input
          type="date"
          className="filter-value-input"
          value={filter.value || ''}
          onChange={(e) => updateFilter(index, { value: e.target.value })}
        />
      );
    }

    // String field (default)
    return (
      <input
        type="text"
        className="filter-value-input"
        placeholder="Enter value"
        value={filter.value || ''}
        onChange={(e) => updateFilter(index, { value: e.target.value })}
      />
    );
  };

  return (
    <div className={`advanced-filter-builder ${className}`}>
      <div className="filter-header">
        <h3>Advanced Filters</h3>
        <button
          type="button"
          className={`logic-toggle ${config.logic.toLowerCase()}`}
          onClick={toggleLogic}
          title="Toggle filter logic"
        >
          {config.logic}
        </button>
      </div>

      {config.filters.length === 0 ? (
        <div className="empty-state">
          <p>No filters added. Click "Add Filter" to get started.</p>
        </div>
      ) : (
        <div className="filters-list">
          {config.filters.map((filter, index) => (
            <div key={index} className="filter-row">
              <div className="filter-number">{index + 1}</div>

              <select
                className="filter-field-select"
                value={filter.field}
                onChange={(e) => {
                  const newField = e.target.value;
                  const availableOps = getAvailableOperators(newField);
                  updateFilter(index, {
                    field: newField,
                    operator: availableOps[0]?.value || 'equals',
                    value: '',
                  });
                }}
              >
                {availableFields.map((field) => (
                  <option key={field.value} value={field.value}>
                    {field.label}
                  </option>
                ))}
              </select>

              <select
                className="filter-operator-select"
                value={filter.operator}
                onChange={(e) => updateFilter(index, { operator: e.target.value as FilterOperator })}
              >
                {getAvailableOperators(filter.field).map((op) => (
                  <option key={op.value} value={op.value}>
                    {op.label}
                  </option>
                ))}
              </select>

              {renderValueInput(filter, index)}

              <button
                type="button"
                className="filter-remove-btn"
                onClick={() => removeFilter(index)}
                title="Remove filter"
              >
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      <button type="button" className="add-filter-btn" onClick={addFilter}>
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path
            fillRule="evenodd"
            d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
            clipRule="evenodd"
          />
        </svg>
        Add Filter
      </button>

      {/* Sort Configuration */}
      <div className="sort-section">
        <h4>Sort Results</h4>
        <div className="sort-controls">
          <select
            className="sort-field-select"
            value={config.sort?.field || ''}
            onChange={(e) => {
              if (e.target.value) {
                updateSort(e.target.value, config.sort?.order || 'desc');
              } else {
                clearSort();
              }
            }}
          >
            <option value="">No sorting</option>
            {availableFields.map((field) => (
              <option key={field.value} value={field.value}>
                {field.label}
              </option>
            ))}
          </select>

          {config.sort && (
            <select
              className="sort-order-select"
              value={config.sort.order}
              onChange={(e) => updateSort(config.sort!.field, e.target.value as 'asc' | 'desc')}
            >
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedFilterBuilder;
