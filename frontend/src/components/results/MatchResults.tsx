import React, { useState } from 'react';
import type { ConfidenceLevel, MatchResultGroup } from '../../types/catalog';
import { VirtualizedTable, type ColumnConfig } from '../common/VirtualizedTable';
import { ExportButton } from '../common/ExportButton';
import { ConfidenceIndicator } from './ConfidenceIndicator';

interface MatchResultsProps {
  results: MatchResultGroup[];
  onMatchClick?: (group: MatchResultGroup, matchIndex: number) => void;
  onExport?: (format: 'csv' | 'excel') => Promise<void>;
  confidenceFilter?: ConfidenceLevel | null;
  onConfidenceFilterChange?: (level: ConfidenceLevel | null) => void;
  loading?: boolean;
  className?: string;
}

export const MatchResults: React.FC<MatchResultsProps> = ({
  results,
  onMatchClick,
  onExport,
  confidenceFilter,
  onConfidenceFilterChange,
  loading = false,
  className = '',
}) => {
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set());

  // Flatten results for table display
  const flattenedResults = results.flatMap((group, groupIndex) => {
    const isExpanded = expandedGroups.has(groupIndex);

    const items: any[] = [
      {
        type: 'group',
        groupIndex,
        isExpanded,
        uploadedTrack: group.uploaded_track,
        matchCount: group.matches.length,
        topMatch: group.matches[0],
      },
    ];

    if (isExpanded) {
      group.matches.forEach((match, matchIndex) => {
        items.push({
          type: 'match',
          groupIndex,
          matchIndex,
          match,
          uploadedTrack: group.uploaded_track,
        });
      });
    }

    return items;
  });

  const toggleGroup = (groupIndex: number) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupIndex)) {
      newExpanded.delete(groupIndex);
    } else {
      newExpanded.add(groupIndex);
    }
    setExpandedGroups(newExpanded);
  };

  const columns: ColumnConfig<any>[] = [
    {
      key: 'track',
      header: 'Uploaded Track',
      width: 300,
      sortable: false,
      render: (item) => {
        if (item.type === 'group') {
          return (
            <div className="track-cell group">
              <button
                type="button"
                className="expand-button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleGroup(item.groupIndex);
                }}
                aria-label={item.isExpanded ? 'Collapse matches' : 'Expand matches'}
              >
                <svg
                  className={`expand-icon ${item.isExpanded ? 'expanded' : ''}`}
                  width="12"
                  height="12"
                  viewBox="0 0 12 12"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M3 5l3 3 3-3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
              <div className="track-info">
                <div className="track-title">{item.uploadedTrack.title}</div>
                <div className="track-artist">
                  {item.uploadedTrack.artist ||
                    item.uploadedTrack.composer ||
                    item.uploadedTrack.writer ||
                    'Unknown Artist'}
                </div>
                <div className="match-count">{item.matchCount} matches found</div>
              </div>
            </div>
          );
        } else {
          return <div className="track-cell match-detail">Match details</div>;
        }
      },
    },
    {
      key: 'matched_work',
      header: 'Matched Work',
      width: 300,
      sortable: false,
      render: (item) => {
        if (item.type === 'group' && item.topMatch) {
          return (
            <div className="work-cell">
              <div className="work-title">{item.topMatch.matched_work.title}</div>
              {item.topMatch.matched_work.iswc && (
                <div className="work-iswc">ISWC: {item.topMatch.matched_work.iswc}</div>
              )}
            </div>
          );
        } else if (item.type === 'match') {
          return (
            <div className="work-cell">
              <div className="work-title">{item.match.matched_work.title}</div>
              {item.match.matched_work.alternate_titles &&
                item.match.matched_work.alternate_titles.length > 0 && (
                  <div className="work-alternates">
                    Also: {item.match.matched_work.alternate_titles.join(', ')}
                  </div>
                )}
              {item.match.matched_work.iswc && (
                <div className="work-iswc">ISWC: {item.match.matched_work.iswc}</div>
              )}
              {item.match.matched_work.contributors && (
                <div className="work-contributors">
                  {item.match.matched_work.contributors
                    .map((c: any) => `${c.name} (${c.role})`)
                    .join(', ')}
                </div>
              )}
            </div>
          );
        }
        return null;
      },
    },
    {
      key: 'confidence',
      header: 'Confidence',
      width: 200,
      sortable: true,
      accessor: (item) => (item.type === 'match' ? item.match.match_score : item.topMatch?.match_score || 0),
      render: (item) => {
        const match = item.type === 'match' ? item.match : item.topMatch;
        if (!match) return null;

        return (
          <ConfidenceIndicator
            level={match.confidence_level}
            score={match.match_score}
            rank={item.type === 'match' ? match.rank : undefined}
            showRank={item.type === 'match'}
            size="small"
          />
        );
      },
    },
  ];

  return (
    <div className={`match-results ${className}`}>
      <div className="results-header">
        <div className="results-info">
          <h2 className="results-title">Match Results</h2>
          <p className="results-count">
            {results.length} tracks with {results.reduce((sum, g) => sum + g.matches.length, 0)}{' '}
            total matches
          </p>
        </div>

        <div className="results-actions">
          {onConfidenceFilterChange && (
            <div className="confidence-filter">
              <label htmlFor="confidence-select" className="filter-label">
                Filter by confidence:
              </label>
              <select
                id="confidence-select"
                value={confidenceFilter || ''}
                onChange={(e) =>
                  onConfidenceFilterChange(
                    e.target.value ? (e.target.value as ConfidenceLevel) : null
                  )
                }
                className="confidence-select"
              >
                <option value="">All</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          )}

          {onExport && <ExportButton onExport={onExport} />}
        </div>
      </div>

      <VirtualizedTable
        data={flattenedResults}
        columns={columns}
        rowHeight={80}
        height={600}
        loading={loading}
        emptyMessage="No matches found"
        onRowClick={(item) => {
          if (item.type === 'match' && onMatchClick) {
            const group = results[item.groupIndex];
            onMatchClick(group, item.matchIndex);
          }
        }}
      />
    </div>
  );
};
