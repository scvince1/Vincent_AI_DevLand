import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { COLORS, sentimentColor } from '../../theme';
import type { AspectTrend } from '../../types';

interface Props {
  data: AspectTrend[];
  height?: number;
  horizontal?: boolean;
}

export function TopicBarChart({ data, height = 240, horizontal = false }: Props) {
  const chartData = data.map((a) => ({
    name: a.aspect.replace(/_/g, ' '),
    mentions: a.mention_count,
    score: a.avg_score,
    label: (a.avg_score > 0.2 ? 'positive' : a.avg_score < -0.2 ? 'negative' : 'neutral') as import('../../theme').SentimentColor,
  }));

  if (horizontal) {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
          <XAxis type="number" tick={{ fill: COLORS.textTertiary, fontSize: 11 }} />
          <YAxis dataKey="name" type="category" tick={{ fill: COLORS.textSecondary, fontSize: 11 }} width={120} />
          <Tooltip
            contentStyle={{
              background: COLORS.bgSurfaceRaised,
              border: `1px solid ${COLORS.border}`,
              color: COLORS.textPrimary,
              fontSize: 12,
            }}
          />
          <Bar dataKey="mentions" name="Mentions" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={sentimentColor(entry.label)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} margin={{ top: 8, right: 16, left: -16, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis dataKey="name" tick={{ fill: COLORS.textSecondary, fontSize: 11 }} angle={-35} textAnchor="end" />
        <YAxis tick={{ fill: COLORS.textTertiary, fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: COLORS.bgSurfaceRaised,
            border: `1px solid ${COLORS.border}`,
            color: COLORS.textPrimary,
            fontSize: 12,
          }}
        />
        <Bar dataKey="mentions" name="Mentions" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={sentimentColor(entry.label)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
