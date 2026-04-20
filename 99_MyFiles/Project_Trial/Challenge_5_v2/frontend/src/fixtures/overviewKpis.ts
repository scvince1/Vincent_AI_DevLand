import type { components } from '../types/api';

type OverviewKPIs = components['schemas']['OverviewKPIs'];
type TimeseriesResponse = components['schemas']['TimeseriesResponse'];
type ShareOfVoiceResponse = components['schemas']['ShareOfVoiceResponse'];

export const FIXTURE_KPI_SUMMARY: OverviewKPIs = {
  total_mentions: 14823,
  overall_score: 0.28,
  wow_delta: -0.04,
  top_rising_negative: ['mop_pad', 'battery', 'app'],
  top_rising_positive: ['suction', 'navigation', 'uv_detection'],
};

function makeDateStr(daysAgo: number): string {
  const d = new Date('2026-04-11');
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString().split('T')[0];
}

export const FIXTURE_SENTIMENT_TIMESERIES: TimeseriesResponse = {
  series: Array.from({ length: 90 }, (_, i) => {
    const daysAgo = 89 - i;
    const base = 0.28;
    const noiseFactor = Math.sin(i * 0.3) * 0.05 + (Math.random() - 0.5) * 0.04;
    const mopDip = daysAgo < 10 ? -0.08 : 0;
    const score = Math.max(-1, Math.min(1, base + noiseFactor + mopDip));
    return {
      date: makeDateStr(daysAgo),
      score: parseFloat(score.toFixed(3)),
      mention_count: Math.floor(150 + Math.random() * 50),
    };
  }),
  brand: null,
  category: null,
};

export const FIXTURE_SHARE_OF_VOICE: ShareOfVoiceResponse = {
  total_mentions: 14823,
  brands: [
    { brand: 'shark', mention_count: 6240, share: 0.421 },
    { brand: 'ninja', mention_count: 3890, share: 0.262 },
    { brand: 'dyson', mention_count: 2380, share: 0.161 },
    { brand: 'irobot', mention_count: 1280, share: 0.086 },
    { brand: 'roborock', mention_count: 1033, share: 0.070 },
  ],
};
