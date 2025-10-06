/**
 * DualChartPanel Component
 *
 * Displays two charts side by side with optional tab navigation for different views.
 * Features:
 * - Tab navigation for switching between chart types or time periods
 * - Responsive layout (side-by-side on desktop, stacked on mobile)
 * - Loading and empty states
 * - Flexible chart rendering via render props or children
 * - Title and description support
 */

import React, { useState } from 'react';
import '../../styles/components/DualChartPanel.css';

export interface ChartTabConfig {
  id: string;
  label: string;
  leftChart: React.ReactNode;
  rightChart: React.ReactNode;
}

export interface DualChartPanelProps {
  title?: string;
  description?: string;
  tabs?: ChartTabConfig[];
  leftChart?: React.ReactNode;
  rightChart?: React.ReactNode;
  leftTitle?: string;
  rightTitle?: string;
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  className?: string;
}

const DualChartPanel: React.FC<DualChartPanelProps> = ({
  title,
  description,
  tabs,
  leftChart,
  rightChart,
  leftTitle,
  rightTitle,
  loading = false,
  error,
  emptyMessage = 'No data available',
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState<string>(tabs?.[0]?.id || '');

  // Determine which charts to render
  const currentLeftChart = tabs
    ? tabs.find((tab) => tab.id === activeTab)?.leftChart
    : leftChart;
  const currentRightChart = tabs
    ? tabs.find((tab) => tab.id === activeTab)?.rightChart
    : rightChart;

  const renderLoadingState = () => (
    <div className="dual-chart-panel__loading">
      <div className="dual-chart-panel__chart-container">
        <div className="skeleton dual-chart-panel__chart-skeleton" />
      </div>
      <div className="dual-chart-panel__chart-container">
        <div className="skeleton dual-chart-panel__chart-skeleton" />
      </div>
    </div>
  );

  const renderErrorState = () => (
    <div className="dual-chart-panel__error">
      <svg
        className="dual-chart-panel__error-icon"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
      <p className="dual-chart-panel__error-message">{error}</p>
    </div>
  );

  const renderEmptyState = () => (
    <div className="dual-chart-panel__empty">
      <svg
        className="dual-chart-panel__empty-icon"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z"
          clipRule="evenodd"
        />
      </svg>
      <p className="dual-chart-panel__empty-message">{emptyMessage}</p>
    </div>
  );

  const hasData = !loading && !error && (currentLeftChart || currentRightChart);

  return (
    <div className={`dual-chart-panel ${className}`}>
      {/* Header */}
      {(title || description || tabs) && (
        <div className="dual-chart-panel__header">
          <div className="dual-chart-panel__header-content">
            {title && <h2 className="dual-chart-panel__title">{title}</h2>}
            {description && (
              <p className="dual-chart-panel__description">{description}</p>
            )}
          </div>

          {/* Tabs */}
          {tabs && tabs.length > 0 && (
            <div className="dual-chart-panel__tabs" role="tablist">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  aria-controls={`panel-${tab.id}`}
                  className={`dual-chart-panel__tab ${
                    activeTab === tab.id ? 'dual-chart-panel__tab--active' : ''
                  }`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Charts Content */}
      <div
        className="dual-chart-panel__content"
        role="tabpanel"
        id={`panel-${activeTab}`}
      >
        {loading && renderLoadingState()}
        {error && renderErrorState()}
        {!hasData && !loading && !error && renderEmptyState()}

        {hasData && (
          <div className="dual-chart-panel__charts">
            {currentLeftChart && (
              <div className="dual-chart-panel__chart-container">
                {leftTitle && (
                  <h3 className="dual-chart-panel__chart-title">{leftTitle}</h3>
                )}
                <div className="dual-chart-panel__chart">{currentLeftChart}</div>
              </div>
            )}

            {currentRightChart && (
              <div className="dual-chart-panel__chart-container">
                {rightTitle && (
                  <h3 className="dual-chart-panel__chart-title">{rightTitle}</h3>
                )}
                <div className="dual-chart-panel__chart">{currentRightChart}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DualChartPanel;
