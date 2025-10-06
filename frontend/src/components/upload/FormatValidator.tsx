import React from 'react';

interface FormatRequirement {
  field: string;
  required: boolean;
  description: string;
  example: string;
}

const FORMAT_REQUIREMENTS: FormatRequirement[] = [
  {
    field: 'title',
    required: true,
    description: 'Track or work title',
    example: 'Yesterday',
  },
  {
    field: 'artist / composer / writer',
    required: true,
    description: 'Artist, composer, or writer name (at least one)',
    example: 'The Beatles',
  },
  {
    field: 'duration',
    required: false,
    description: 'Track duration in seconds or MM:SS format',
    example: '125 or 02:05',
  },
  {
    field: 'iswc',
    required: false,
    description: 'International Standard Musical Work Code',
    example: 'T-034.524.680-1',
  },
  {
    field: 'year',
    required: false,
    description: 'Release or creation year',
    example: '1965',
  },
];

interface FormatValidatorProps {
  onDownloadTemplate?: () => void;
  className?: string;
}

export const FormatValidator: React.FC<FormatValidatorProps> = ({
  onDownloadTemplate,
  className = '',
}) => {
  return (
    <div className={`format-validator ${className}`}>
      <div className="validator-header">
        <h3 className="validator-title">File Format Requirements</h3>
        {onDownloadTemplate && (
          <button type="button" onClick={onDownloadTemplate} className="template-button">
            <svg
              className="download-icon"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M8 2v8M8 10l-3-3M8 10l3-3M3 14h10"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Download Template
          </button>
        )}
      </div>

      <div className="requirements-list">
        <table className="requirements-table">
          <thead>
            <tr>
              <th>Field</th>
              <th>Required</th>
              <th>Description</th>
              <th>Example</th>
            </tr>
          </thead>
          <tbody>
            {FORMAT_REQUIREMENTS.map((req) => (
              <tr key={req.field}>
                <td className="field-name">
                  <code>{req.field}</code>
                </td>
                <td className="field-required">
                  {req.required ? (
                    <span className="badge required">Required</span>
                  ) : (
                    <span className="badge optional">Optional</span>
                  )}
                </td>
                <td className="field-description">{req.description}</td>
                <td className="field-example">
                  <code>{req.example}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="format-examples">
        <h4 className="examples-title">Supported Formats</h4>

        <div className="format-tabs">
          <details className="format-detail" open>
            <summary className="format-summary">CSV Example</summary>
            <div className="format-content">
              <pre className="code-block">
                {`title,artist,duration,iswc,year
Yesterday,The Beatles,125,T-034.524.680-1,1965
Let It Be,The Beatles,243,T-010.109.656-6,1970
Hey Jude,The Beatles,431,T-010.358.302-1,1968`}
              </pre>
            </div>
          </details>

          <details className="format-detail">
            <summary className="format-summary">JSON Example</summary>
            <div className="format-content">
              <pre className="code-block">
                {`[
  {
    "title": "Yesterday",
    "artist": "The Beatles",
    "duration": 125,
    "iswc": "T-034.524.680-1",
    "year": 1965
  },
  {
    "title": "Let It Be",
    "composer": "Paul McCartney",
    "duration": "04:03",
    "year": 1970
  }
]`}
              </pre>
            </div>
          </details>

          <details className="format-detail">
            <summary className="format-summary">XML Example</summary>
            <div className="format-content">
              <pre className="code-block">
                {`<?xml version="1.0" encoding="UTF-8"?>
<catalog>
  <track>
    <title>Yesterday</title>
    <artist>The Beatles</artist>
    <duration>125</duration>
    <iswc>T-034.524.680-1</iswc>
    <year>1965</year>
  </track>
</catalog>`}
              </pre>
            </div>
          </details>
        </div>
      </div>

      <div className="validator-notes">
        <h4 className="notes-title">Notes</h4>
        <ul className="notes-list">
          <li>Column/field names are case-insensitive</li>
          <li>Duration can be in seconds (integer) or MM:SS format</li>
          <li>ISWC format: T-DDD.DDD.DDD-C (validation is flexible)</li>
          <li>The system will attempt to match tracks even with incomplete metadata</li>
          <li>Better metadata quality leads to more accurate matches</li>
        </ul>
      </div>
    </div>
  );
};
