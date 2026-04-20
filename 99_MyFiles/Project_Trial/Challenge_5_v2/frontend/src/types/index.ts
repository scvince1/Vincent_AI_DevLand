/**
 * Re-exports all domain type aliases so components can use short imports
 * (`from '../types'`). Types were previously appended to types/api.ts but
 * gen:types wipes that file on every regen. Sourced from api/endpoints.ts
 * instead, which wraps components['schemas'][...] in stable named aliases.
 */
export type {
  Brand,
  Category,
  SourcePlatform,
  SentimentLabel,
  Polarity,
  Mention,
  MentionListResponse,
  OverviewKPIs,
  TimeseriesPoint,
  TimeseriesResponse,
  BrandShare,
  ShareOfVoiceResponse,
  ProductSummary,
  ProductAspectResponse,
  AspectTrend,
  PlatformComparisonResponse,
  PlatformAspectCell,
  TopicExplorerResponse,
  TopicCluster,
  ComparativeTopicResponse,
  ShareOfAspect,
  AlertListResponse,
  AlertEvent,
} from '../api/endpoints';
