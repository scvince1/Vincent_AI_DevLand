import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { AspectTrend } from '../../types';
import { COLORS } from '../../theme';

interface Props {
  aspects: AspectTrend[];
  categoryAvg?: AspectTrend[];
  height?: number;
}

export function AspectRadarChart({ aspects, categoryAvg, height = 280 }: Props) {
  const data = aspects.map((a) => {
    const avg = categoryAvg?.find((ca) => ca.aspect === a.aspect);
    return {
      aspect: a.aspect.replace(/_/g, ' '),
      product: Math.round((a.avg_score + 1) * 50), // normalize -1..1 to 0..100
      category: avg ? Math.round((avg.avg_score + 1) * 50) : undefined,
    };
  });

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={data}>
        <PolarGrid stroke={COLORS.border} />
        <PolarAngleAxis
          dataKey="aspect"
          tick={{ fill: COLORS.textSecondary, fontSize: 11 }}
        />
        <PolarRadiusAxis domain={[0, 100]} tick={{ fill: COLORS.textTertiary, fontSize: 10 }} />
        <Radar name="Product" dataKey="product" stroke={COLORS.accent} fill={COLORS.accent} fillOpacity={0.25} />
        {categoryAvg && (
          <Radar name="Category avg" dataKey="category" stroke={COLORS.neutral} fill={COLORS.neutral} fillOpacity={0.12} />
        )}
        <Legend wrapperStyle={{ fontSize: 12, color: COLORS.textSecondary }} />
        <Tooltip
          contentStyle={{
            background: COLORS.bgSurfaceRaised,
            border: `1px solid ${COLORS.border}`,
            color: COLORS.textPrimary,
            fontSize: 12,
          }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
