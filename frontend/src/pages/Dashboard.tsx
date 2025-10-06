/**
 * Enhanced Dashboard Page
 *
 * Main dashboard view with improved UI components and real-time data integration.
 * Integrates: StatCard, DualChartPanel, ActivityFeed, SavedSearchPanel
 */

import React, { lazy, Suspense } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api';
import StatCard from '../components/dashboard/StatCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import SavedSearchPanel from '../components/dashboard/SavedSearchPanel';
import type { ActivityItem } from '../components/dashboard/ActivityFeed';
import type { SavedSearch } from '../components/dashboard/SavedSearchPanel';
import '../styles/pages/Dashboard.css';

// Lazy load chart components with recharts library to reduce initial bundle size (-324 KB)
const MonthlyTrendCharts = lazy(() => import('../components/dashboard/MonthlyTrendCharts'));
const DistributionPieCharts = lazy(() => import('../components/dashboard/DistributionPieCharts'));

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Fetch statistics
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ['statistics'],
    queryFn: () => apiClient.getStatistics(),
  });

  // Fetch MLC business metrics
  const {
    data: mlcStats,
    isLoading: mlcStatsLoading,
  } = useQuery({
    queryKey: ['mlc-statistics'],
    queryFn: () => apiClient.getMLCStatistics(),
  });

  // Fetch recent uploads for activity feed
  const {
    data: uploads,
    isLoading: uploadsLoading,
  } = useQuery({
    queryKey: ['recent-uploads'],
    queryFn: () => apiClient.getCatalogUploads({ page: 1, limit: 5 }),
  });

  // TODO: Fetch from new activity logs API when available
  const activities: ActivityItem[] = React.useMemo(() => {
    if (!uploads?.data) return [];

    return uploads.data.map((upload) => ({
      id: String(upload.id),
      user_email: upload.publisher_name || 'system',
      action: 'catalog.upload',
      description: `uploaded catalog "${upload.filename}"`,
      status: upload.status === 'completed' ? 'success' : upload.status === 'failed' ? 'failure' : 'pending',
      created_at: upload.created_at,
    }));
  }, [uploads]);

  // TODO: Fetch from user preferences API when available
  const [savedSearches] = React.useState<SavedSearch[]>([]);

  // TODO: Replace with real trend data from backend API
  // Mock 7-day trend data for sparklines
  const mockTrendData = {
    unmatchedRecordings: [
      { value: 450 }, { value: 445 }, { value: 470 }, { value: 455 },
      { value: 465 }, { value: 460 }, { value: 456 }
    ],
    unclaimedShares: [
      { value: 120 }, { value: 118 }, { value: 115 }, { value: 117 },
      { value: 114 }, { value: 112 }, { value: 110 }
    ],
    lowConfidence: [
      { value: 85 }, { value: 88 }, { value: 82 }, { value: 90 },
      { value: 87 }, { value: 86 }, { value: 89 }
    ],
    claimsThisMonth: [
      { value: 10 }, { value: 12 }, { value: 15 }, { value: 18 },
      { value: 22 }, { value: 25 }, { value: 28 }
    ]
  };

  const handleApplySavedSearch = (search: SavedSearch) => {
    console.log('Applying saved search:', search);
    // TODO: Navigate to works browser with applied filters
  };

  const handleDeleteSavedSearch = (searchId: string) => {
    console.log('Deleting saved search:', searchId);
    // TODO: Implement API call to delete search
  };

  const handleCreateSavedSearch = () => {
    console.log('Create new saved search');
    // TODO: Open modal or navigate to search creation
  };

  const handleFilterClick = (filter: 'has_iswc' | 'disputed', value: boolean) => {
    // Navigate to works browser with filter applied
    const params = new URLSearchParams();
    params.set(filter === 'has_iswc' ? 'has_iswc' : 'has_disputed_rights', String(value));
    navigate(`/works?${params.toString()}`);
  };

  const loading = statsLoading || uploadsLoading || mlcStatsLoading;
  const error = statsError;

  if (error) {
    return (
      <div className="dashboard dashboard--error">
        <div className="dashboard__error">
          <svg className="dashboard__error-icon" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <h2>Failed to load dashboard</h2>
          <p>Please try again later</p>
          <button className="btn btn-primary" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Page Header */}
      <div className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Dashboard</h1>
          <p className="dashboard__subtitle">Overview of your music catalog and recent activity</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="dashboard__stats">
        <StatCard
          title="Total Works"
          value={stats?.total_works.toLocaleString() || '0'}
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
              <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
            </svg>
          }
          iconColor="primary"
          loading={loading}
        />

        <StatCard
          title="Works with ISWC"
          value={stats?.works_with_iswc.toLocaleString() || '0'}
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path
                fillRule="evenodd"
                d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          }
          iconColor="success"
          description={`${stats?.works_with_iswc_percentage.toFixed(1)}% of total`}
          loading={loading}
        />

        <StatCard
          title="Disputed Rights"
          value={stats?.disputed_works.toLocaleString() || '0'}
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          }
          iconColor="warning"
          description={`${stats?.disputed_works_percentage.toFixed(1)}% of total`}
          loading={loading}
        />

        <StatCard
          title="Recent Uploads"
          value={uploads?.data.length || '0'}
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 4.414V13a1 1 0 11-2 0V4.414L7.707 6.707a1 1 0 01-1.414 0z"
                clipRule="evenodd"
              />
            </svg>
          }
          iconColor="neutral"
          description="in the last 7 days"
          loading={loading}
        />
      </div>

      {/* MLC Business Metrics Section */}
      <div style={{ marginTop: '32px' }}>
        <h2 className="dashboard__section-title" style={{
          fontSize: 'var(--font-size-lg)',
          fontWeight: 'var(--font-weight-semibold)',
          color: 'var(--text-primary)',
          marginBottom: '16px'
        }}>
          MLC Royalty Recovery
        </h2>
        <div className="dashboard__stats">
          <StatCard
            title="Unmatched Recordings"
            value={mlcStats?.unmatched_recordings.toLocaleString() || '0'}
            icon={
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            }
            iconColor="warning"
            sparklineData={mockTrendData.unmatchedRecordings}
            description={`$${mlcStats?.estimated_unclaimed_value.toLocaleString() || '0'} potential recovery`}
            loading={loading}
          />

          <StatCard
            title="Unclaimed Shares"
            value={mlcStats?.unclaimed_shares.toLocaleString() || '0'}
            icon={
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            }
            iconColor="error"
            sparklineData={mockTrendData.unclaimedShares}
            description={`${mlcStats?.unclaimed_percentage.toFixed(1) || '0'}% of works`}
            loading={loading}
          />

          <StatCard
            title="Low Confidence Matches"
            value={mlcStats?.low_confidence_matches.toLocaleString() || '0'}
            icon={
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            }
            iconColor="neutral"
            sparklineData={mockTrendData.lowConfidence}
            description="Require manual review"
            loading={loading}
          />

          <StatCard
            title="Claims This Month"
            value={mlcStats?.claims_submitted.toLocaleString() || '0'}
            icon={
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            }
            iconColor="success"
            sparklineData={mockTrendData.claimsThisMonth}
            description={`$${mlcStats?.claims_value.toLocaleString() || '0'} submitted`}
            loading={loading}
          />
        </div>
      </div>

      {/* Charts Section - Lazy loaded to reduce initial bundle by 324 KB */}
      {stats?.monthly_trend && stats.monthly_trend.length > 0 && (
        <div className="dashboard__charts">
          <Suspense fallback={
            <div style={{
              background: 'var(--bg-secondary)',
              borderRadius: '8px',
              padding: '24px',
              minHeight: '400px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-tertiary)'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div className="loading-spinner" style={{ margin: '0 auto 12px' }}></div>
                <p>Loading charts...</p>
              </div>
            </div>
          }>
            <MonthlyTrendCharts
              data={stats.monthly_trend}
              loading={loading}
            />
          </Suspense>
        </div>
      )}

      {/* Distribution Pie Charts - Interactive ISWC and Disputed Works Visualization */}
      {stats && (
        <Suspense fallback={
          <div style={{
            background: 'var(--bg-secondary)',
            borderRadius: '12px',
            padding: '24px',
            marginTop: '32px',
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-tertiary)'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div className="loading-spinner" style={{ margin: '0 auto 12px' }}></div>
              <p>Loading distribution charts...</p>
            </div>
          </div>
        }>
          <DistributionPieCharts
            data={{
              total_works: stats.total_works,
              works_with_iswc: stats.works_with_iswc,
              disputed_works: stats.disputed_works,
            }}
            onFilterClick={handleFilterClick}
          />
        </Suspense>
      )}

      {/* Activity and Searches Grid */}
      <div className="dashboard__grid">
        <div className="dashboard__activity">
          <ActivityFeed
            activities={activities}
            loading={uploadsLoading}
            maxItems={5}
            emptyMessage="No recent catalog uploads"
          />
        </div>

        <div className="dashboard__searches">
          <SavedSearchPanel
            searches={savedSearches}
            onApply={handleApplySavedSearch}
            onDelete={handleDeleteSavedSearch}
            onCreate={handleCreateSavedSearch}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
};
