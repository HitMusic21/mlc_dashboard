import React from 'react';

export type UploadStatus = 'uploading' | 'processing' | 'completed' | 'failed';

interface UploadProgressProps {
  status: UploadStatus;
  progress: number; // 0-100
  tracksProcessed?: number;
  totalTracks?: number;
  estimatedTimeRemaining?: number; // in seconds
  errorMessage?: string;
  onCancel?: () => void;
  className?: string;
}

export const UploadProgress: React.FC<UploadProgressProps> = ({
  status,
  progress,
  tracksProcessed = 0,
  totalTracks = 0,
  estimatedTimeRemaining,
  errorMessage,
  onCancel,
  className = '',
}) => {
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`;
  };

  const getStatusLabel = (): string => {
    switch (status) {
      case 'uploading':
        return 'Uploading file...';
      case 'processing':
        return 'Processing catalog...';
      case 'completed':
        return 'Completed!';
      case 'failed':
        return 'Failed';
      default:
        return 'Processing...';
    }
  };

  const getStatusColor = (): string => {
    switch (status) {
      case 'uploading':
        return 'blue';
      case 'processing':
        return 'blue';
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  const isActive = status === 'uploading' || status === 'processing';
  const canCancel = isActive && onCancel;

  return (
    <div className={`upload-progress ${className}`} data-status={status}>
      {/* Status header */}
      <div className="progress-header">
        <div className="status-info">
          {status === 'failed' ? (
            <svg
              className="status-icon error"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path
                d="M15 9l-6 6M9 9l6 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          ) : status === 'completed' ? (
            <svg
              className="status-icon success"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path
                d="M8 12l3 3 5-5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          ) : (
            <svg
              className="status-icon loading"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" opacity="0.25" />
              <path
                d="M12 2a10 10 0 0110 10"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          )}
          <span className="status-label">{getStatusLabel()}</span>
        </div>

        {canCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="cancel-button"
            aria-label="Cancel upload"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress bar */}
      <div className="progress-bar-container">
        <div
          className={`progress-bar ${getStatusColor()}`}
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {/* Progress details */}
      <div className="progress-details">
        <div className="progress-stats">
          <span className="progress-percentage">{Math.round(progress)}%</span>

          {totalTracks > 0 && (
            <span className="tracks-info">
              {tracksProcessed.toLocaleString()} / {totalTracks.toLocaleString()} tracks
            </span>
          )}

          {isActive && estimatedTimeRemaining !== undefined && estimatedTimeRemaining > 0 && (
            <span className="time-remaining">
              ~{formatTime(estimatedTimeRemaining)} remaining
            </span>
          )}
        </div>
      </div>

      {/* Error message */}
      {status === 'failed' && errorMessage && (
        <div className="error-message" role="alert">
          <svg
            className="error-icon"
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="2" />
            <path d="M8 4v5M8 11v1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
