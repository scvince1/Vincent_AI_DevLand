import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { TimeseriesPoint } from '../../types';
import { COLORS } from '../../theme';

interface Props {
  data: TimeseriesPoint[];
  height?: number;
}

export function SentimentLineChart({ data, height = 260 }: Props) {
  const tickStyle = { fill: COLORS.textTertiary, fontSize: 11 };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis
          dataKey="date"
          tick={tickStyle}
          tickFormatter={(v: string) => v.slice(5)}
          interval="preserveStartEnd"
        />
        <YAxis tick={tickStyle} domain={[-1, 1]} />
        <Tooltip
          contentStyle={{
            background: COLORS.bgSurfaceRaised,
            border: `1px solid ${COLORS.border}`,
            color: COLORS.textPrimary,
            fontSize: 12,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: COLORS.textSecondary }} />
        <Line
          type="monotone"
          dataKey="score"
          stroke={COLORS.accent}
          strokeWidth={2}
          dot={false}
          name="Sentiment Score"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
