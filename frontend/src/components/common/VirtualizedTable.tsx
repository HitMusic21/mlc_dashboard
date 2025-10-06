import React, { useMemo, useState } from 'react';
import { List } from 'react-window';

export interface ColumnConfig<T> {
  key: string;
  header: string;
  width?: number;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
  accessor?: (item: T) => any;
}

interface VirtualizedTableProps<T> {
  data: T[];
  columns: ColumnConfig<T>[];
  rowHeight?: number;
  height?: number;
  width?: string | number;
  onRowClick?: (item: T, index: number) => void;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

type SortDirection = 'asc' | 'desc' | null;

export function VirtualizedTable<T extends Record<string, any>>({
  data,
  columns,
  rowHeight = 50,
  height = 600,
  width = '100%',
  onRowClick,
  loading = false,
  emptyMessage = 'No data available',
  className = '',
}: VirtualizedTableProps<T>) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) {
      return data;
    }

    const column = columns.find((c) => c.key === sortColumn);
    if (!column) {
      return data;
    }

    return [...data].sort((a, b) => {
      const aValue = column.accessor ? column.accessor(a) : a[sortColumn];
      const bValue = column.accessor ? column.accessor(b) : b[sortColumn];

      if (aValue === bValue) return 0;

      const comparison = aValue > bValue ? 1 : -1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection, columns]);

  const handleSort = (columnKey: string, sortable: boolean = true) => {
    if (!sortable) return;

    if (sortColumn === columnKey) {
      // Cycle through: asc -> desc -> null
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortColumn(null);
        setSortDirection(null);
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const Row = React.useCallback(
    ({ index, style }: any) => {
      const item = sortedData[index];

      return (
        <div
          style={style}
          className={`table-row ${onRowClick ? 'clickable' : ''}`}
          onClick={() => onRowClick?.(item, index)}
          role={onRowClick ? 'button' : undefined}
          tabIndex={onRowClick ? 0 : undefined}
          onKeyDown={(e) => {
            if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
              e.preventDefault();
              onRowClick(item, index);
            }
          }}
        >
          {columns.map((column) => (
            <div
              key={column.key}
              className="table-cell"
              style={{ width: column.width || 'auto', flex: column.width ? undefined : 1 }}
            >
              {column.render ? column.render(item) : item[column.key]}
            </div>
          ))}
        </div>
      );
    },
    [sortedData, columns, onRowClick]
  );

  if (loading) {
    return (
      <div className={`virtualized-table loading ${className}`}>
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={`virtualized-table empty ${className}`}>
        <div className="empty-message">{emptyMessage}</div>
      </div>
    );
  }

  return (
    <div className={`virtualized-table ${className}`} style={{ width }}>
      {/* Header */}
      <div className="table-header">
        {columns.map((column) => (
          <div
            key={column.key}
            className={`table-header-cell ${column.sortable !== false ? 'sortable' : ''} ${
              sortColumn === column.key ? `sorted-${sortDirection}` : ''
            }`}
            style={{ width: column.width || 'auto', flex: column.width ? undefined : 1 }}
            onClick={() => handleSort(column.key, column.sortable !== false)}
            role={column.sortable !== false ? 'button' : undefined}
            tabIndex={column.sortable !== false ? 0 : undefined}
            onKeyDown={(e) => {
              if (column.sortable !== false && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                handleSort(column.key, true);
              }
            }}
          >
            <span>{column.header}</span>
            {column.sortable !== false && (
              <span className="sort-indicator" aria-hidden="true">
                {sortColumn === column.key ? (
                  sortDirection === 'asc' ? (
                    '↑'
                  ) : (
                    '↓'
                  )
                ) : (
                  <span className="sort-placeholder">⇅</span>
                )}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Virtualized rows */}
      <List
        defaultHeight={height}
        rowCount={sortedData.length}
        rowHeight={rowHeight}
        overscanCount={5}
        rowComponent={Row}
        rowProps={{}}
      />
    </div>
  );
}
