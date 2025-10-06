import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SearchBar } from '../components/common/SearchBar';
import { FilterPanel, type FilterConfig } from '../components/common/FilterPanel';
import { VirtualizedTable, type ColumnConfig } from '../components/common/VirtualizedTable';
import { apiClient } from '../services/api';
import { usePreferencesStore, selectItemsPerPage } from '../stores/usePreferencesStore';
import type { MusicalWork } from '../types/works';

export const WorksBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterConfig>({});
  const [page, setPage] = useState(1);
  const [selectedWork, setSelectedWork] = useState<MusicalWork | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  const limit = usePreferencesStore(selectItemsPerPage);

  // Fetch works
  const {
    data: worksResponse,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['works', page, limit, searchQuery, filters],
    queryFn: () =>
      apiClient.getWorks({
        page,
        limit,
        search: searchQuery || undefined,
        has_iswc: filters.has_iswc,
        has_disputed_rights: filters.has_disputed_rights,
        created_after: filters.created_after,
        created_before: filters.created_before,
      }),
    placeholderData: (previousData) => previousData,
  });

  const columns: ColumnConfig<MusicalWork>[] = [
    {
      key: 'title',
      header: 'Title',
      width: 300,
      sortable: true,
      render: (work) => (
        <div className="work-title-cell">
          <div className="work-title">{work.title}</div>
          {work.alternate_titles && work.alternate_titles.length > 0 && (
            <div className="work-alternates">
              Also: {work.alternate_titles.slice(0, 2).join(', ')}
              {work.alternate_titles.length > 2 && '...'}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'contributors',
      header: 'Contributors',
      width: 200,
      sortable: false,
      render: (work) => (
        <div className="contributors-cell">
          {work.contributors ? (
            <span title={work.contributors}>{work.contributors}</span>
          ) : (
            <span className="text-muted">—</span>
          )}
        </div>
      ),
    },
    {
      key: 'publisher',
      header: 'Publisher',
      width: 200,
      sortable: true,
      render: (work) =>
        work.publisher ? (
          <span className="publisher-name">{work.publisher}</span>
        ) : (
          <span className="text-muted">—</span>
        ),
    },
    {
      key: 'iswc',
      header: 'ISWC',
      width: 140,
      sortable: true,
      render: (work) =>
        work.iswc ? (
          <code className="iswc-code">{work.iswc}</code>
        ) : (
          <span className="text-muted">—</span>
        ),
    },
    {
      key: 'territory',
      header: 'Territory',
      width: 100,
      sortable: true,
      render: (work) =>
        work.territory ? (
          <span className="territory-code">{work.territory}</span>
        ) : (
          <span className="text-muted">—</span>
        ),
    },
    {
      key: 'has_disputed_rights',
      header: 'Status',
      width: 120,
      sortable: true,
      render: (work) =>
        work.has_disputed_rights ? (
          <span className="badge warning">Disputed</span>
        ) : (
          <span className="badge success">Clear</span>
        ),
    },
  ];

  const handleWorkClick = (work: MusicalWork) => {
    setSelectedWork(work);
    setIsDetailsOpen(true);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="works-browser-page">
      <div className="page-header">
        <h1 className="page-title">Browse Musical Works</h1>
        <p className="page-subtitle">
          Search and explore {worksResponse?.pagination.total_items.toLocaleString() || '0'}{' '}
          musical works
        </p>
      </div>

      {/* Search and Filters */}
      <div className="browser-controls">
        <div className="search-section">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search by title, contributor, or ISWC..."
            className="works-search"
          />
        </div>

        <FilterPanel
          filters={filters}
          onFilterChange={setFilters}
          onApply={() => setPage(1)}
          onReset={() => {
            setFilters({});
            setPage(1);
          }}
        />
      </div>

      {/* Results */}
      <div className="browser-results">
        {error ? (
          <div className="error-message">
            <p>Failed to load works. Please try again.</p>
          </div>
        ) : (
          <>
            <div className="results-info">
              <p className="results-count">
                Showing {worksResponse?.data.length || 0} of{' '}
                {worksResponse?.pagination.total_items.toLocaleString() || 0} works
              </p>
              {worksResponse?.meta.response_time_ms && (
                <p className="response-time">
                  Response time: {worksResponse.meta.response_time_ms.toFixed(0)}ms
                </p>
              )}
            </div>

            <VirtualizedTable
              data={worksResponse?.data || []}
              columns={columns}
              rowHeight={70}
              height={600}
              loading={isLoading}
              emptyMessage="No works found"
              onRowClick={handleWorkClick}
            />

            {/* Pagination */}
            {worksResponse && worksResponse.pagination.total_pages > 1 && (
              <div className="pagination">
                <button
                  type="button"
                  className="pagination-button"
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </button>

                <div className="pagination-info">
                  Page {page} of {worksResponse.pagination.total_pages}
                </div>

                <button
                  type="button"
                  className="pagination-button"
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page === worksResponse.pagination.total_pages}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Work Details Modal */}
      {isDetailsOpen && selectedWork && (
        <>
          <div
            className="modal-backdrop"
            onClick={() => setIsDetailsOpen(false)}
            role="presentation"
          />
          <div className="work-details-modal" role="dialog" aria-modal="true">
            <div className="modal-header">
              <h2 className="modal-title">{selectedWork.title}</h2>
              <button
                type="button"
                className="modal-close"
                onClick={() => setIsDetailsOpen(false)}
                aria-label="Close"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M18 6L6 18M6 6l12 12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>

            <div className="modal-body">
              <dl className="details-list">
                {selectedWork.iswc && (
                  <div className="detail-row">
                    <dt>ISWC</dt>
                    <dd>
                      <code>{selectedWork.iswc}</code>
                    </dd>
                  </div>
                )}

                {selectedWork.alternate_titles && selectedWork.alternate_titles.length > 0 && (
                  <div className="detail-row">
                    <dt>Alternate Titles</dt>
                    <dd>{selectedWork.alternate_titles.join(', ')}</dd>
                  </div>
                )}

                {selectedWork.contributors && (
                  <div className="detail-row">
                    <dt>Contributors</dt>
                    <dd>{selectedWork.contributors}</dd>
                  </div>
                )}

                {selectedWork.publisher && (
                  <div className="detail-row">
                    <dt>Publisher</dt>
                    <dd className="publisher-name">{selectedWork.publisher}</dd>
                  </div>
                )}

                {selectedWork.territory && (
                  <div className="detail-row">
                    <dt>Territory</dt>
                    <dd><span className="territory-code">{selectedWork.territory}</span></dd>
                  </div>
                )}

                {selectedWork.lyrics_languages && selectedWork.lyrics_languages.length > 0 && (
                  <div className="detail-row">
                    <dt>Languages</dt>
                    <dd>{selectedWork.lyrics_languages.join(', ')}</dd>
                  </div>
                )}

                {selectedWork.country_of_production && (
                  <div className="detail-row">
                    <dt>Country of Production</dt>
                    <dd>{selectedWork.country_of_production}</dd>
                  </div>
                )}

                <div className="detail-row">
                  <dt>Disputed Rights</dt>
                  <dd>
                    {selectedWork.has_disputed_rights ? (
                      <span className="badge warning">Yes</span>
                    ) : (
                      <span className="badge success">No</span>
                    )}
                  </dd>
                </div>

                <div className="detail-row">
                  <dt>Created</dt>
                  <dd>{new Date(selectedWork.created_at).toLocaleString()}</dd>
                </div>
              </dl>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
