/**
 * StatCard Component
 *
 * Displays a key metric with optional trend indicator and comparison text.
 * Features:
 * - Icon support with customizable colors
 * - Value and title display
 * - Optional trend indicator (increase/decrease with percentage)
 * - Optional comparison/description text
 * - Loading skeleton state
 * - Responsive design with mobile optimization
 */

import React from 'react';
import Sparkline, { type SparklineData } from './Sparkline';
import '../../styles/components/StatCard.css';

export interface TrendData {
  direction: 'up' | 'down' | 'neutral';
  percentage: number;
  label?: string; // e.g., "vs last month"
}

export interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  iconColor?: 'primary' | 'success' | 'warning' | 'error' | 'neutral';
  trend?: TrendData;
  sparklineData?: SparklineData[];
  sparklineColor?: string;
  description?: string;
  loading?: boolean;
  className?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  iconColor = 'primary',
  trend,
  sparklineData,
  sparklineColor,
  description,
  loading = false,
  className = '',
}) => {
  if (loading) {
    return (
      <div className={`stat-card stat-card--loading ${className}`}>
        <div className="stat-card__header">
          <div className="skeleton stat-card__icon-skeleton" />
          <div className="stat-card__content">
            <div className="skeleton stat-card__title-skeleton" />
            <div className="skeleton stat-card__value-skeleton" />
          </div>
        </div>
        {description && <div className="skeleton stat-card__description-skeleton" />}
      </div>
    );
  }

  const getTrendIcon = () => {
    if (!trend) return null;

    switch (trend.direction) {
      case 'up':
        return (
          <svg className="stat-card__trend-icon" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'down':
        return (
          <svg className="stat-card__trend-icon" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'neutral':
        return (
          <svg className="stat-card__trend-icon" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      default:
        return null;
    }
  };

  const getTrendClass = () => {
    if (!trend) return '';
    return `stat-card__trend--${trend.direction}`;
  };

  return (
    <div className={`stat-card ${className}`}>
      <div className="stat-card__header">
        {icon && (
          <div className={`stat-card__icon stat-card__icon--${iconColor}`}>
            {icon}
          </div>
        )}
        <div className="stat-card__content">
          <h3 className="stat-card__title">{title}</h3>
          <p className="stat-card__value">{value}</p>
        </div>
      </div>

      {sparklineData && sparklineData.length > 0 && (
        <div className="stat-card__sparkline">
          <Sparkline
            data={sparklineData}
            color={sparklineColor || `var(--color-${iconColor}-600)`}
            height={40}
          />
        </div>
      )}

      {(trend || description) && (
        <div className="stat-card__footer">
          {trend && (
            <div className={`stat-card__trend ${getTrendClass()}`}>
              {getTrendIcon()}
              <span className="stat-card__trend-percentage">
                {trend.percentage}%
              </span>
              {trend.label && (
                <span className="stat-card__trend-label">{trend.label}</span>
              )}
            </div>
          )}
          {description && (
            <p className="stat-card__description">{description}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default StatCard;
