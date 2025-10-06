/**
 * Sparkline Component
 *
 * A minimal line chart showing trend data over time.
 * Used in StatCards to visualize data trends.
 */

import React from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';

export interface SparklineData {
  value: number;
}

export interface SparklineProps {
  data: SparklineData[];
  color?: string;
  height?: number;
}

const Sparkline: React.FC<SparklineProps> = ({
  data,
  color = 'var(--color-primary-600)',
  height = 40,
}) => {
  if (!data || data.length === 0) {
    return null;
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 0, bottom: 5, left: 0 }}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          dot={false}
          animationDuration={300}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default Sparkline;
