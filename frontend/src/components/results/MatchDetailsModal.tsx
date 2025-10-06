import React, { useEffect } from 'react';
import type { CatalogMatch, UploadedTrack } from '../../types/catalog';
import { ConfidenceIndicator } from './ConfidenceIndicator';

interface MatchDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  uploadedTrack: UploadedTrack;
  match: CatalogMatch;
  className?: string;
}

export const MatchDetailsModal: React.FC<MatchDetailsModalProps> = ({
  isOpen,
  onClose,
  uploadedTrack,
  match,
  className = '',
}) => {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = '';
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return 'Unknown';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="modal-backdrop"
        onClick={onClose}
        role="presentation"
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className={`match-details-modal ${className}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">
            Match Details
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="modal-close"
            aria-label="Close modal"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M18 6L6 18M6 6l12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        <div className="modal-body">
          {/* Match Score */}
          <section className="modal-section">
            <h3 className="section-title">Match Score</h3>
            <ConfidenceIndicator
              level={match.confidence_level}
              score={match.match_score}
              rank={match.rank}
              showRank
              size="large"
            />
            <div className="algorithm-info">
              <span className="algorithm-label">Algorithm:</span>
              <code className="algorithm-value">{match.algorithm_used}</code>
            </div>
          </section>

          {/* Uploaded Track Info */}
          <section className="modal-section">
            <h3 className="section-title">Your Uploaded Track</h3>
            <dl className="details-list">
              <div className="detail-row">
                <dt>Title</dt>
                <dd>{uploadedTrack.title}</dd>
              </div>
              {uploadedTrack.artist && (
                <div className="detail-row">
                  <dt>Artist</dt>
                  <dd>{uploadedTrack.artist}</dd>
                </div>
              )}
              {uploadedTrack.composer && (
                <div className="detail-row">
                  <dt>Composer</dt>
                  <dd>{uploadedTrack.composer}</dd>
                </div>
              )}
              {uploadedTrack.writer && (
                <div className="detail-row">
                  <dt>Writer</dt>
                  <dd>{uploadedTrack.writer}</dd>
                </div>
              )}
              {uploadedTrack.duration !== undefined && (
                <div className="detail-row">
                  <dt>Duration</dt>
                  <dd>{formatDuration(uploadedTrack.duration)}</dd>
                </div>
              )}
              {uploadedTrack.iswc && (
                <div className="detail-row">
                  <dt>ISWC</dt>
                  <dd>
                    <code>{uploadedTrack.iswc}</code>
                  </dd>
                </div>
              )}
              {uploadedTrack.year && (
                <div className="detail-row">
                  <dt>Year</dt>
                  <dd>{uploadedTrack.year}</dd>
                </div>
              )}
            </dl>
          </section>

          {/* Matched Work Info */}
          <section className="modal-section">
            <h3 className="section-title">Matched BWARM Work</h3>
            <dl className="details-list">
              <div className="detail-row">
                <dt>Title</dt>
                <dd>{match.matched_work.title}</dd>
              </div>
              {match.matched_work.alternate_titles &&
                match.matched_work.alternate_titles.length > 0 && (
                  <div className="detail-row">
                    <dt>Alternate Titles</dt>
                    <dd>{match.matched_work.alternate_titles.join(', ')}</dd>
                  </div>
                )}
              {match.matched_work.iswc && (
                <div className="detail-row">
                  <dt>ISWC</dt>
                  <dd>
                    <code>{match.matched_work.iswc}</code>
                  </dd>
                </div>
              )}
              {match.matched_work.contributors &&
                match.matched_work.contributors.length > 0 && (
                  <div className="detail-row">
                    <dt>Contributors</dt>
                    <dd>
                      {match.matched_work.contributors
                        .map((c) => `${c.name} (${c.role})`)
                        .join(', ')}
                    </dd>
                  </div>
                )}
              {match.matched_work.lyrics_languages &&
                match.matched_work.lyrics_languages.length > 0 && (
                  <div className="detail-row">
                    <dt>Lyrics Languages</dt>
                    <dd>{match.matched_work.lyrics_languages.join(', ')}</dd>
                  </div>
                )}
              {match.matched_work.country_of_production && (
                <div className="detail-row">
                  <dt>Country of Production</dt>
                  <dd>{match.matched_work.country_of_production}</dd>
                </div>
              )}
              <div className="detail-row">
                <dt>Disputed Rights</dt>
                <dd>
                  {match.matched_work.has_disputed_rights ? (
                    <span className="badge warning">Yes</span>
                  ) : (
                    <span className="badge success">No</span>
                  )}
                </dd>
              </div>
            </dl>
          </section>
        </div>

        <div className="modal-footer">
          <button type="button" onClick={onClose} className="button-secondary">
            Close
          </button>
        </div>
      </div>
    </>
  );
};
