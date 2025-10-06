/**
 * DistributionPieCharts Component
 *
 * Interactive pie charts showing ISWC coverage and disputed rights distribution.
 * Features click-to-filter functionality for data exploration.
 */

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { exportChartAsPNG, createCSVFromData } from '../../utils/chartExport';

interface DistributionData {
  total_works: number;
  works_with_iswc: number;
  disputed_works: number;
}

interface DistributionPieChartsProps {
  data: DistributionData;
  onFilterClick?: (filter: 'has_iswc' | 'disputed', value: boolean) => void;
}

const COLORS = {
  primary: 'var(--color-primary-600)',
  success: 'var(--color-success-600)',
  warning: 'var(--color-warning-600)',
  error: 'var(--color-error-600)',
  neutral: 'var(--color-neutral-400)',
};

const DistributionPieCharts: React.FC<DistributionPieChartsProps> = ({
  data,
  onFilterClick,
}) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  // ISWC Coverage Data
  const iswcData = [
    {
      name: 'With ISWC',
      value: data.works_with_iswc,
      color: COLORS.success,
      filter: { type: 'has_iswc' as const, value: true },
    },
    {
      name: 'Without ISWC',
      value: data.total_works - data.works_with_iswc,
      color: COLORS.neutral,
      filter: { type: 'has_iswc' as const, value: false },
    },
  ];

  // Disputed Rights Data
  const disputedData = [
    {
      name: 'Disputed',
      value: data.disputed_works,
      color: COLORS.error,
      filter: { type: 'disputed' as const, value: true },
    },
    {
      name: 'Non-Disputed',
      value: data.total_works - data.disputed_works,
      color: COLORS.success,
      filter: { type: 'disputed' as const, value: false },
    },
  ];

  const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        style={{ fontSize: '14px', fontWeight: 600 }}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  const handlePieClick = (data: any, index: number, _chartType: 'iswc' | 'disputed') => {
    if (onFilterClick && data.filter) {
      onFilterClick(data.filter.type, data.filter.value);
    }
    setActiveIndex(index);
  };

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      borderRadius: '12px',
      padding: '24px',
      marginTop: '32px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
      }}>
        <div>
          <h2 style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: 'var(--font-weight-semibold)',
            color: 'var(--text-primary)',
            marginBottom: '4px',
          }}>
            Works Distribution
          </h2>
          <p style={{
            fontSize: 'var(--font-size-sm)',
            color: 'var(--text-secondary)',
          }}>
            Click segments to filter works by category
          </p>
        </div>
        <button
          onClick={() => {
            const combinedData = [
              ...iswcData.map(d => ({ category: 'ISWC', name: d.name, value: d.value })),
              ...disputedData.map(d => ({ category: 'Rights', name: d.name, value: d.value }))
            ];
            createCSVFromData(combinedData, 'works-distribution.csv');
          }}
          style={{
            padding: '8px 16px',
            background: 'var(--color-primary-600)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 'var(--font-weight-medium)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'var(--color-primary-700)';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'var(--color-primary-600)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          Export CSV
        </button>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '32px',
      }}>
        {/* ISWC Coverage Chart */}
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
          }}>
            <h3 style={{
              fontSize: 'var(--font-size-base)',
              fontWeight: 'var(--font-weight-medium)',
              color: 'var(--text-primary)',
              margin: 0,
            }}>
              ISWC Coverage
            </h3>
            <button
              onClick={() => exportChartAsPNG('iswc-chart', 'iswc-coverage.png')}
              style={{
                padding: '6px 12px',
                background: 'transparent',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-primary)',
                borderRadius: '6px',
                fontSize: 'var(--font-size-xs)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'var(--bg-tertiary)';
                e.currentTarget.style.borderColor = 'var(--color-primary-600)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = 'var(--border-primary)';
              }}
              title="Export as PNG"
            >
              <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
              </svg>
              PNG
            </button>
          </div>
          <div id="iswc-chart">
            <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={iswcData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                onClick={(data, index) => handlePieClick(data, index, 'iswc')}
                style={{ cursor: onFilterClick ? 'pointer' : 'default' }}
              >
                {iswcData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    opacity={activeIndex === null || activeIndex === index ? 1 : 0.5}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '16px',
            marginTop: '16px',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--text-secondary)',
          }}>
            <div>
              <strong style={{ color: COLORS.success }}>
                {((data.works_with_iswc / data.total_works) * 100).toFixed(1)}%
              </strong>{' '}
              with ISWC
            </div>
            <div>
              <strong style={{ color: COLORS.neutral }}>
                {(((data.total_works - data.works_with_iswc) / data.total_works) * 100).toFixed(1)}%
              </strong>{' '}
              without ISWC
            </div>
          </div>
        </div>

        {/* Disputed Rights Chart */}
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
          }}>
            <h3 style={{
              fontSize: 'var(--font-size-base)',
              fontWeight: 'var(--font-weight-medium)',
              color: 'var(--text-primary)',
              margin: 0,
            }}>
              Rights Status
            </h3>
            <button
              onClick={() => exportChartAsPNG('disputed-chart', 'rights-status.png')}
              style={{
                padding: '6px 12px',
                background: 'transparent',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-primary)',
                borderRadius: '6px',
                fontSize: 'var(--font-size-xs)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'var(--bg-tertiary)';
                e.currentTarget.style.borderColor = 'var(--color-primary-600)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = 'var(--border-primary)';
              }}
              title="Export as PNG"
            >
              <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
              </svg>
              PNG
            </button>
          </div>
          <div id="disputed-chart">
            <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={disputedData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                onClick={(data, index) => handlePieClick(data, index, 'disputed')}
                style={{ cursor: onFilterClick ? 'pointer' : 'default' }}
              >
                {disputedData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    opacity={activeIndex === null || activeIndex === index ? 1 : 0.5}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '16px',
            marginTop: '16px',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--text-secondary)',
          }}>
            <div>
              <strong style={{ color: COLORS.error }}>
                {((data.disputed_works / data.total_works) * 100).toFixed(1)}%
              </strong>{' '}
              disputed
            </div>
            <div>
              <strong style={{ color: COLORS.success }}>
                {(((data.total_works - data.disputed_works) / data.total_works) * 100).toFixed(1)}%
              </strong>{' '}
              clear
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DistributionPieCharts;
