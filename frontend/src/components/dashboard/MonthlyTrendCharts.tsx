/**
 * MonthlyTrendCharts Component
 *
 * Lazy-loaded chart component to reduce initial bundle size.
 * Contains recharts library (324 KB) which is code-split for better performance.
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import DualChartPanel from './DualChartPanel';

interface MonthlyDataPoint {
  month: string;
  count: number;
}

interface MonthlyTrendChartsProps {
  data: MonthlyDataPoint[];
  loading?: boolean;
}

const MonthlyTrendCharts: React.FC<MonthlyTrendChartsProps> = ({ data, loading = false }) => {
  const chartConfig = {
    grid: { strokeDasharray: '3 3', stroke: 'var(--border-primary)' },
    axis: { stroke: 'var(--text-tertiary)' },
    tooltip: {
      contentStyle: {
        backgroundColor: 'var(--bg-primary)',
        border: '1px solid var(--border-primary)',
      },
    },
  };

  const lineChart = (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid {...chartConfig.grid} />
        <XAxis dataKey="month" {...chartConfig.axis} />
        <YAxis {...chartConfig.axis} />
        <Tooltip {...chartConfig.tooltip} />
        <Legend />
        <Line
          type="monotone"
          dataKey="count"
          stroke="var(--color-primary-600)"
          strokeWidth={2}
          name="New Works"
          dot={{ fill: 'var(--color-primary-600)' }}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  const barChart = (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid {...chartConfig.grid} />
        <XAxis dataKey="month" {...chartConfig.axis} />
        <YAxis {...chartConfig.axis} />
        <Tooltip {...chartConfig.tooltip} />
        <Legend />
        <Bar
          dataKey="count"
          fill="var(--color-primary-600)"
          name="Works Count"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );

  return (
    <DualChartPanel
      title="Upload Analytics"
      description="Track upload trends and catalog performance"
      tabs={[
        {
          id: 'trend',
          label: 'Monthly Trend',
          leftChart: lineChart,
          rightChart: barChart,
        },
      ]}
      loading={loading}
    />
  );
};

export default MonthlyTrendCharts;
