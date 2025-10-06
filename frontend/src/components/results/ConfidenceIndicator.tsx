import React from 'react';
import type { ConfidenceLevel } from '../../types/catalog';

interface ConfidenceIndicatorProps {
  level: ConfidenceLevel;
  score: number;
  rank?: number;
  showScore?: boolean;
  showRank?: boolean;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  level,
  score,
  rank,
  showScore = true,
  showRank = false,
  size = 'medium',
  className = '',
}) => {
  const getColorClass = (): string => {
    switch (level) {
      case 'high':
        return 'confidence-high';
      case 'medium':
        return 'confidence-medium';
      case 'low':
        return 'confidence-low';
      default:
        return 'confidence-unknown';
    }
  };

  const getLevelLabel = (): string => {
    switch (level) {
      case 'high':
        return 'High';
      case 'medium':
        return 'Medium';
      case 'low':
        return 'Low';
      default:
        return 'Unknown';
    }
  };

  const getRankLabel = (): string => {
    if (!rank) return '';
    if (rank === 1) return '1st';
    if (rank === 2) return '2nd';
    if (rank === 3) return '3rd';
    return `${rank}th`;
  };

  const scorePercentage = Math.round(score * 100);

  return (
    <div className={`confidence-indicator ${getColorClass()} size-${size} ${className}`}>
      <div className="confidence-badge">
        <span className="confidence-level">{getLevelLabel()}</span>
        {showScore && <span className="confidence-score">{scorePercentage}%</span>}
      </div>

      {showScore && (
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{ width: `${scorePercentage}%` }}
            role="progressbar"
            aria-valuenow={scorePercentage}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Match confidence: ${scorePercentage}%`}
          />
        </div>
      )}

      {showRank && rank && (
        <div className="confidence-rank">
          <span className="rank-badge">{getRankLabel()}</span>
        </div>
      )}
    </div>
  );
};
