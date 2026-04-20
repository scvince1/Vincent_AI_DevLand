import type { components } from '../types/api';

type PlatformComparisonResponse = components['schemas']['PlatformComparisonResponse'];
type PlatformAspectCell = components['schemas']['PlatformAspectCell'];

// Grid cells: platform x aspect sentiment
const cells: PlatformAspectCell[] = [
  // Reddit — skews technical and sarcastic
  { platform: 'reddit', aspect: 'navigation', sentiment_score: 0.71, mention_count: 612 },
  { platform: 'reddit', aspect: 'suction', sentiment_score: 0.78, mention_count: 589 },
  { platform: 'reddit', aspect: 'app', sentiment_score: -0.45, mention_count: 498 },
  { platform: 'reddit', aspect: 'mop_pad', sentiment_score: -0.68, mention_count: 421 },
  { platform: 'reddit', aspect: 'firmware', sentiment_score: -0.35, mention_count: 312 },
  // Amazon — skews packaging/value
  { platform: 'amazon', aspect: 'suction', sentiment_score: 0.82, mention_count: 891 },
  { platform: 'amazon', aspect: 'ease_of_use', sentiment_score: 0.68, mention_count: 756 },
  { platform: 'amazon', aspect: 'value', sentiment_score: 0.35, mention_count: 623 },
  { platform: 'amazon', aspect: 'mop_pad', sentiment_score: -0.72, mention_count: 287 },
  { platform: 'amazon', aspect: 'noise', sentiment_score: -0.18, mention_count: 201 },
  // YouTube — skews aspirational
  { platform: 'youtube', aspect: 'suction', sentiment_score: 0.85, mention_count: 398 },
  { platform: 'youtube', aspect: 'uv_detection', sentiment_score: 0.88, mention_count: 312 },
  { platform: 'youtube', aspect: 'design', sentiment_score: 0.72, mention_count: 287 },
  { platform: 'youtube', aspect: 'noise', sentiment_score: -0.32, mention_count: 245 },
  { platform: 'youtube', aspect: 'battery', sentiment_score: -0.28, mention_count: 201 },
  // Trustpilot — skews post-purchase
  { platform: 'trustpilot', aspect: 'customer_service', sentiment_score: -0.42, mention_count: 512 },
  { platform: 'trustpilot', aspect: 'warranty', sentiment_score: -0.55, mention_count: 421 },
  { platform: 'trustpilot', aspect: 'durability', sentiment_score: -0.38, mention_count: 312 },
  { platform: 'trustpilot', aspect: 'suction', sentiment_score: 0.75, mention_count: 289 },
  { platform: 'trustpilot', aspect: 'value', sentiment_score: 0.45, mention_count: 245 },
];

export const FIXTURE_PLATFORM_COMPARISON: PlatformComparisonResponse = {
  grid: cells,
  top_topics_by_platform: {
    reddit: ['mop_pad', 'firmware', 'app', 'navigation', 'suction'],
    amazon: ['suction', 'ease_of_use', 'value', 'mop_pad', 'noise'],
    youtube: ['suction', 'uv_detection', 'design', 'noise', 'battery'],
    trustpilot: ['customer_service', 'warranty', 'durability', 'suction', 'value'],
  },
};
