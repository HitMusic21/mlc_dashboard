import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { MatchResults } from '../components/results/MatchResults';
import { MatchDetailsModal } from '../components/results/MatchDetailsModal';
import { apiClient } from '../services/api';
import { usePreferencesStore, selectItemsPerPage } from '../stores/usePreferencesStore';
import type { ConfidenceLevel, MatchResultGroup } from '../types/catalog';

export const ResultsViewer: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const [page, setPage] = useState(1);
  const [confidenceFilter, setConfidenceFilter] = useState<ConfidenceLevel | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<{
    group: MatchResultGroup;
    matchIndex: number;
  } | null>(null);

  const limit = usePreferencesStore(selectItemsPerPage);

  // Fetch upload info
  const { data: uploadInfo } = useQuery({
    queryKey: ['upload-info', uploadId],
    queryFn: () => apiClient.getUploadStatus(Number(uploadId)),
    enabled: !!uploadId,
  });

  // Fetch results
  const {
    data: resultsResponse,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['upload-results', uploadId, page, limit, confidenceFilter],
    queryFn: () =>
      apiClient.getUploadResults(Number(uploadId), {
        page,
        limit,
        confidence: confidenceFilter || undefined,
      }),
    enabled: !!uploadId,
    placeholderData: (previousData) => previousData,
  });

  const handleExport = async (format: 'csv' | 'excel') => {
    if (!uploadId) return;

    try {
      const blob = await apiClient.exportUploadResults(Number(uploadId), format, {
        confidence: confidenceFilter || undefined,
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `matches-${uploadId}.${format === 'csv' ? 'csv' : 'xlsx'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleMatchClick = (group: MatchResultGroup, matchIndex: number) => {
    setSelectedMatch({ group, matchIndex });
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!uploadId) {
    return (
      <div className="error-page">
        <p>Invalid upload ID</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-page">
        <p>Failed to load results. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="results-viewer-page">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Match Results</h1>
          {uploadInfo && (
            <div className="upload-info">
              <p className="upload-filename">{uploadInfo.filename}</p>
              <p className="upload-meta">
                {uploadInfo.publisher_name} •{' '}
                {new Date(uploadInfo.created_at).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>

        {uploadInfo?.processing_stats && (
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Tracks</span>
              <span className="stat-value">
                {uploadInfo.processing_stats.total_tracks.toLocaleString()}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Matches</span>
              <span className="stat-value">
                {uploadInfo.processing_stats.total_matches.toLocaleString()}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">High</span>
              <span className="stat-value confidence-high">
                {uploadInfo.processing_stats.high_confidence_matches.toLocaleString()}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Medium</span>
              <span className="stat-value confidence-medium">
                {uploadInfo.processing_stats.medium_confidence_matches.toLocaleString()}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Low</span>
              <span className="stat-value confidence-low">
                {uploadInfo.processing_stats.low_confidence_matches.toLocaleString()}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Match Results */}
      <div className="results-content">
        <MatchResults
          results={resultsResponse?.data || []}
          onMatchClick={handleMatchClick}
          onExport={handleExport}
          confidenceFilter={confidenceFilter}
          onConfidenceFilterChange={setConfidenceFilter}
          loading={isLoading}
        />

        {/* Pagination */}
        {resultsResponse && resultsResponse.pagination.total_pages > 1 && (
          <div className="pagination">
            <button
              type="button"
              className="pagination-button"
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1 || isLoading}
            >
              Previous
            </button>

            <div className="pagination-info">
              Page {page} of {resultsResponse.pagination.total_pages}
            </div>

            <button
              type="button"
              className="pagination-button"
              onClick={() => handlePageChange(page + 1)}
              disabled={page === resultsResponse.pagination.total_pages || isLoading}
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Match Details Modal */}
      {selectedMatch && (
        <MatchDetailsModal
          isOpen={!!selectedMatch}
          onClose={() => setSelectedMatch(null)}
          uploadedTrack={selectedMatch.group.uploaded_track}
          match={selectedMatch.group.matches[selectedMatch.matchIndex]}
        />
      )}
    </div>
  );
};
