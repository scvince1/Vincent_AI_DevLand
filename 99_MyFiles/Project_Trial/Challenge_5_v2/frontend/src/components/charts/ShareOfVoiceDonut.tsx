import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { BrandShare } from '../../types';
import { COLORS } from '../../theme';

const BRAND_PALETTE = [COLORS.accent, COLORS.positive, COLORS.neutral, COLORS.negative, COLORS.mixed, '#06b6d4', '#ec4899'];

interface Props {
  data: BrandShare[];
  height?: number;
}

export function ShareOfVoiceDonut({ data, height = 220 }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius="55%"
          outerRadius="80%"
          dataKey="mention_count"
          nameKey="brand"
          strokeWidth={0}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={BRAND_PALETTE[i % BRAND_PALETTE.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number, name: string) => [`${value.toLocaleString()} mentions`, name]}
          contentStyle={{
            background: COLORS.bgSurfaceRaised,
            border: `1px solid ${COLORS.border}`,
            color: COLORS.textPrimary,
            fontSize: 12,
          }}
        />
        <Legend
          wrapperStyle={{ fontSize: 12, color: COLORS.textSecondary }}
          formatter={(value: string, entry: unknown) => {
            const share = (entry as { payload?: BrandShare })?.payload?.share ?? 0;
            return `${value} (${(share * 100).toFixed(1)}%)`;
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
