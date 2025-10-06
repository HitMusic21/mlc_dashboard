import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const ALLOWED_TYPES = {
  'text/csv': ['.csv'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/json': ['.json'],
  'text/xml': ['.xml'],
  'application/xml': ['.xml'],
};

const MAX_SIZE_BYTES = 500 * 1024 * 1024; // 500MB
const MAX_SIZE_MB = 500;

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  className?: string;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  onFileSelect,
  disabled = false,
  className = '',
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > MAX_SIZE_BYTES) {
      return `File too large. Maximum size is ${MAX_SIZE_MB}MB. Your file is ${(
        file.size /
        1024 /
        1024
      ).toFixed(2)}MB.`;
    }

    // Check file type
    const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;
    const isValidType = Object.values(ALLOWED_TYPES)
      .flat()
      .includes(extension);

    if (!isValidType) {
      return `Invalid file type. Allowed types: CSV, Excel (.xls, .xlsx), JSON, XML`;
    }

    return null;
  };

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError(null);

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === 'file-too-large') {
          setError(`File too large. Maximum size is ${MAX_SIZE_MB}MB.`);
        } else if (rejection.errors[0]?.code === 'file-invalid-type') {
          setError('Invalid file type. Allowed types: CSV, Excel, JSON, XML');
        } else {
          setError(rejection.errors[0]?.message || 'File validation failed');
        }
        return;
      }

      if (acceptedFiles.length === 0) {
        setError('No file selected');
        return;
      }

      const file = acceptedFiles[0];
      const validationError = validateFile(file);

      if (validationError) {
        setError(validationError);
        return;
      }

      setSelectedFile(file);
      setError(null);
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ALLOWED_TYPES,
    maxSize: MAX_SIZE_BYTES,
    maxFiles: 1,
    disabled,
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  return (
    <div className={`file-uploader ${className}`}>
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'drag-active' : ''} ${
          disabled ? 'disabled' : ''
        } ${error ? 'error' : ''} ${selectedFile ? 'has-file' : ''}`}
      >
        <input {...getInputProps()} aria-label="File upload" />

        <div className="dropzone-content">
          {selectedFile ? (
            <>
              <svg
                className="file-icon success"
                width="48"
                height="48"
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20M28 8l12 12M28 8v12h12"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M18 30l4 4 8-8"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="file-details">
                <p className="file-name">{selectedFile.name}</p>
                <p className="file-size">{formatFileSize(selectedFile.size)}</p>
              </div>
              <p className="dropzone-hint">Click or drag to replace file</p>
            </>
          ) : (
            <>
              <svg
                className="upload-icon"
                width="48"
                height="48"
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20M28 8l12 12M28 8v12h12M24 24v12M24 24l-4 4M24 24l4 4"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              {isDragActive ? (
                <p className="dropzone-message">Drop your file here</p>
              ) : (
                <>
                  <p className="dropzone-message">
                    <span className="primary-text">Click to upload</span> or drag and drop
                  </p>
                  <p className="dropzone-hint">CSV, Excel, JSON, or XML (max {MAX_SIZE_MB}MB)</p>
                </>
              )}
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="upload-error" role="alert">
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
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
