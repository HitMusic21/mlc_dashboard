import React, { useState } from 'react';

export type ExportFormat = 'csv' | 'excel';

interface ExportButtonProps {
  onExport: (format: ExportFormat) => Promise<void>;
  disabled?: boolean;
  className?: string;
}

export const ExportButton: React.FC<ExportButtonProps> = ({
  onExport,
  disabled = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingFormat, setLoadingFormat] = useState<ExportFormat | null>(null);

  const handleExport = async (format: ExportFormat) => {
    setIsLoading(true);
    setLoadingFormat(format);
    setIsOpen(false);

    try {
      await onExport(format);
    } catch (error) {
      console.error(`Export failed for format ${format}:`, error);
      // Error handling could be enhanced with toast notifications
    } finally {
      setIsLoading(false);
      setLoadingFormat(null);
    }
  };

  const toggleDropdown = () => {
    if (!disabled && !isLoading) {
      setIsOpen(!isOpen);
    }
  };

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.export-button-wrapper')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className={`export-button-wrapper ${className}`}>
      <button
        type="button"
        className={`export-button ${isOpen ? 'open' : ''}`}
        onClick={toggleDropdown}
        disabled={disabled || isLoading}
        aria-label="Export data"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        {isLoading ? (
          <>
            <svg
              className="export-icon loading"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M10 2a8 8 0 100 16 8 8 0 000-16z"
                stroke="currentColor"
                strokeWidth="2"
                opacity="0.3"
              />
              <path
                d="M10 2a8 8 0 018 8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            <span>Exporting {loadingFormat?.toUpperCase()}...</span>
          </>
        ) : (
          <>
            <svg
              className="export-icon"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M10 2v10M10 12l-4-4M10 12l4-4M3 16h14"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span>Export</span>
            <svg
              className="dropdown-arrow"
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M3 5l3 3 3-3"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </>
        )}
      </button>

      {isOpen && !isLoading && (
        <div className="export-dropdown" role="menu">
          <button
            type="button"
            className="export-option"
            onClick={() => handleExport('csv')}
            role="menuitem"
          >
            <svg
              className="format-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <rect x="2" y="2" width="12" height="12" rx="1" stroke="currentColor" strokeWidth="2" />
              <path d="M2 6h12M6 2v12" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            <span>CSV Format</span>
          </button>

          <button
            type="button"
            className="export-option"
            onClick={() => handleExport('excel')}
            role="menuitem"
          >
            <svg
              className="format-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <rect x="2" y="2" width="12" height="12" rx="1" stroke="currentColor" strokeWidth="2" />
              <text
                x="8"
                y="11"
                fontSize="8"
                textAnchor="middle"
                fill="currentColor"
                fontWeight="bold"
              >
                X
              </text>
            </svg>
            <span>Excel Format</span>
          </button>
        </div>
      )}
    </div>
  );
};
