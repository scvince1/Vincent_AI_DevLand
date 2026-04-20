// Palette constants for use in Recharts (which needs string color values, not CSS vars)
export const COLORS = {
  bgBase: '#0d0f14',
  bgSurface: '#161b24',
  bgSurfaceRaised: '#1e2533',
  border: '#2a3347',
  textPrimary: '#e8ecf4',
  textSecondary: '#8b96ab',
  textTertiary: '#6b7a94',
  accent: '#4f8ef7',
  positive: '#3ecf8e',
  neutral: '#f0b429',
  negative: '#f05252',
  mixed: '#a78bfa',
  severityLow: '#f0b429',
  severityMedium: '#f97316',
  severityHigh: '#f05252',
} as const;

export type SentimentColor = 'positive' | 'neutral' | 'negative' | 'mixed';

export function sentimentColor(label: SentimentColor): string {
  return COLORS[label];
}
