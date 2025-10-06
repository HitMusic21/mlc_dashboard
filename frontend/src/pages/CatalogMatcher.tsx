import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileUploader } from '../components/upload/FileUploader';
import { UploadProgress } from '../components/upload/UploadProgress';
import { FormatValidator } from '../components/upload/FormatValidator';
import { useFileUpload } from '../hooks/useFileUpload';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import type { UploadStatus } from '../types/catalog';

export const CatalogMatcher: React.FC = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [publisherName, setPublisherName] = useState('');
  const [uploadId, setUploadId] = useState<number | null>(null);
  const [pollingEnabled, setPollingEnabled] = useState(false);

  const { uploadFile, isUploading, progress, error, reset } = useFileUpload();

  // Poll upload status while processing
  const { data: uploadStatus } = useQuery({
    queryKey: ['upload-status', uploadId],
    queryFn: () => apiClient.getUploadStatus(uploadId!),
    enabled: pollingEnabled && uploadId !== null,
    refetchInterval: 1000, // Poll every second
  });

  // Handle upload status changes (replaces onSuccess callback)
  React.useEffect(() => {
    if (uploadStatus) {
      // Stop polling when completed or failed
      if (uploadStatus.status === 'completed' || uploadStatus.status === 'failed') {
        setPollingEnabled(false);

        // Navigate to results if completed
        if (uploadStatus.status === 'completed') {
          setTimeout(() => {
            navigate(`/results/${uploadId}`);
          }, 2000);
        }
      }
    }
  }, [uploadStatus, uploadId, navigate]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    reset();
  };

  const handleUpload = async () => {
    if (!selectedFile || !publisherName.trim()) {
      return;
    }

    const result = await uploadFile(selectedFile, publisherName.trim());

    if (result) {
      setUploadId(result.id);
      setPollingEnabled(true);
    }
  };

  const handleCancel = () => {
    setPollingEnabled(false);
    reset();
    setSelectedFile(null);
    setUploadId(null);
  };

  const canUpload = selectedFile && publisherName.trim() && !isUploading;

  return (
    <div className="catalog-matcher-page">
      <div className="page-header">
        <h1 className="page-title">Catalog Matcher</h1>
        <p className="page-subtitle">
          Upload your catalog to match against BWARM's musical works database
        </p>
      </div>

      <div className="matcher-content">
        {/* Upload Section */}
        <div className="upload-section">
          <div className="section-card">
            <h2 className="section-title">Upload Catalog File</h2>

            {/* Publisher Name Input */}
            <div className="form-group">
              <label htmlFor="publisher-name" className="form-label">
                Publisher Name
              </label>
              <input
                id="publisher-name"
                type="text"
                value={publisherName}
                onChange={(e) => setPublisherName(e.target.value)}
                placeholder="Enter publisher name"
                className="form-input"
                disabled={isUploading || pollingEnabled}
              />
            </div>

            {/* File Uploader */}
            <FileUploader
              onFileSelect={handleFileSelect}
              disabled={isUploading || pollingEnabled}
            />

            {/* Upload Button */}
            {selectedFile && !isUploading && !uploadId && (
              <button
                type="button"
                onClick={handleUpload}
                disabled={!canUpload}
                className="button-primary upload-button"
              >
                Start Matching
              </button>
            )}

            {/* Upload Progress */}
            {(isUploading || uploadStatus) && (
              <UploadProgress
                status={(uploadStatus?.status as UploadStatus) || 'uploading'}
                progress={uploadStatus?.progress_percentage || progress}
                tracksProcessed={uploadStatus?.processing_stats?.total_tracks || 0}
                totalTracks={uploadStatus?.processing_stats?.total_tracks || 0}
                estimatedTimeRemaining={uploadStatus?.estimated_time_remaining_seconds}
                errorMessage={error || undefined}
                onCancel={pollingEnabled ? handleCancel : undefined}
              />
            )}

            {/* Processing Stats */}
            {uploadStatus?.status === 'completed' && uploadStatus.processing_stats && (
              <div className="processing-stats">
                <h3 className="stats-title">Processing Complete!</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">Total Tracks</span>
                    <span className="stat-value">
                      {uploadStatus.processing_stats.total_tracks.toLocaleString()}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Matches Found</span>
                    <span className="stat-value">
                      {uploadStatus.processing_stats.total_matches.toLocaleString()}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">High Confidence</span>
                    <span className="stat-value confidence-high">
                      {uploadStatus.processing_stats.high_confidence_matches.toLocaleString()}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Medium Confidence</span>
                    <span className="stat-value confidence-medium">
                      {uploadStatus.processing_stats.medium_confidence_matches.toLocaleString()}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Low Confidence</span>
                    <span className="stat-value confidence-low">
                      {uploadStatus.processing_stats.low_confidence_matches.toLocaleString()}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Processing Time</span>
                    <span className="stat-value">
                      {uploadStatus.processing_stats.processing_time_seconds.toFixed(1)}s
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => navigate(`/results/${uploadId}`)}
                  className="button-primary view-results-button"
                >
                  View Results
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Format Information */}
        <div className="info-section">
          <div className="section-card">
            <FormatValidator onDownloadTemplate={() => console.log('Download template')} />
          </div>

          <div className="section-card help-card">
            <h3 className="section-title">How It Works</h3>
            <ol className="help-steps">
              <li>
                <strong>Prepare your catalog</strong> - Export your music catalog in CSV, Excel,
                JSON, or XML format
              </li>
              <li>
                <strong>Upload the file</strong> - Drag and drop or click to select your catalog
                file (max 500MB)
              </li>
              <li>
                <strong>Wait for processing</strong> - Our matching engine analyzes each track
                against BWARM's database
              </li>
              <li>
                <strong>Review matches</strong> - Explore match results with confidence scores and
                detailed information
              </li>
              <li>
                <strong>Export results</strong> - Download your matches in CSV or Excel format
              </li>
            </ol>
          </div>

          <div className="section-card tips-card">
            <h3 className="section-title">Tips for Better Matching</h3>
            <ul className="tips-list">
              <li>Include ISWC codes when available for exact matches</li>
              <li>Provide accurate track durations in seconds or MM:SS format</li>
              <li>Use consistent artist/composer naming conventions</li>
              <li>Include year information to improve matching accuracy</li>
              <li>Remove duplicate tracks before uploading</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
