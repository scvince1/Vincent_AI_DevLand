/**
 * API endpoint functions — typed against the generated types from api-contract.yaml.
 * All shapes reference components["schemas"][...] via the convenience aliases below.
 */
import { apiFetch, USE_FIXTURES } from './client';
import type { components } from '../types/api';

// Convenience aliases so call sites read cleanly
export type OverviewKPIs = components['schemas']['OverviewKPIs'];
export type TimeseriesPoint = components['schemas']['TimeseriesPoint'];
export type TimeseriesResponse = components['schemas']['TimeseriesResponse'];
export type ShareOfVoiceResponse = components['schemas']['ShareOfVoiceResponse'];
export type BrandShare = components['schemas']['BrandShare'];
export type ProductSummary = components['schemas']['ProductSummary'];
export type ProductAspectResponse = components['schemas']['ProductAspectResponse'];
export type AspectTrend = components['schemas']['AspectTrend'];
export type PlatformComparisonResponse = components['schemas']['PlatformComparisonResponse'];
export type PlatformAspectCell = components['schemas']['PlatformAspectCell'];
export type TopicExplorerResponse = components['schemas']['TopicExplorerResponse'];
export type TopicCluster = components['schemas']['TopicCluster'];
export type ComparativeTopicResponse = components['schemas']['ComparativeTopicResponse'];
export type ShareOfAspect = components['schemas']['ShareOfAspect'];
export type AlertListResponse = components['schemas']['AlertListResponse'];
export type AlertEvent = components['schemas']['AlertEvent'];
export type Mention = components['schemas']['Mention'];
export type MentionListResponse = components['schemas']['MentionListResponse'];
export type Brand = components['schemas']['Brand'];
export type Category = components['schemas']['Category'];
export type SourcePlatform = components['schemas']['SourcePlatform'];
export type SentimentLabel = components['schemas']['SentimentLabel'];
export type Polarity = components['schemas']['Polarity'];

// Fixture imports
import {
  FIXTURE_KPI_SUMMARY,
  FIXTURE_SENTIMENT_TIMESERIES,
  FIXTURE_SHARE_OF_VOICE,
} from '../fixtures/overviewKpis';
import { FIXTURE_PRODUCTS, FIXTURE_PRODUCT_ASPECTS, getProductByModel } from '../fixtures/products';
import { FIXTURE_PLATFORM_COMPARISON } from '../fixtures/platformBreakdown';
import { FIXTURE_TOPIC_EXPLORER, FIXTURE_TOPIC_COMPARATIVE } from '../fixtures/topicClusters';
import { FIXTURE_ALERTS } from '../fixtures/alerts';
import { FIXTURE_MENTIONS } from '../fixtures/mentions';

// --- Overview ---

export async function fetchKpiSummary(brand?: Brand, category?: Category): Promise<OverviewKPIs> {
  if (USE_FIXTURES) return FIXTURE_KPI_SUMMARY;
  return apiFetch<OverviewKPIs>('/api/overview/kpis', { brand, category });
}

export async function fetchSentimentTimeseries(brand?: Brand, category?: Category): Promise<TimeseriesResponse> {
  if (USE_FIXTURES) return FIXTURE_SENTIMENT_TIMESERIES;
  return apiFetch<TimeseriesResponse>('/api/overview/timeseries', { brand, category });
}

export async function fetchShareOfVoice(category?: Category): Promise<ShareOfVoiceResponse> {
  if (USE_FIXTURES) return FIXTURE_SHARE_OF_VOICE;
  return apiFetch<ShareOfVoiceResponse>('/api/overview/share_of_voice', { category });
}

// --- Products ---

export async function fetchProducts(brand?: Brand, category?: Category): Promise<ProductSummary[]> {
  if (USE_FIXTURES) {
    let products = FIXTURE_PRODUCTS;
    if (brand) products = products.filter((p) => p.brand === brand);
    if (category) products = products.filter((p) => p.category === category);
    return products;
  }
  return apiFetch<ProductSummary[]>('/api/products', { brand, category });
}

export async function fetchProductAspects(model: string): Promise<ProductAspectResponse> {
  if (USE_FIXTURES) return getProductByModel(model) ?? FIXTURE_PRODUCT_ASPECTS[0];
  return apiFetch<ProductAspectResponse>(`/api/products/${encodeURIComponent(model)}/aspects`);
}

export async function fetchProductTimeseries(model: string): Promise<TimeseriesResponse> {
  if (USE_FIXTURES) {
    const product = getProductByModel(model);
    const sparkline = product?.aspects[0]?.sparkline ?? [];
    return {
      series: sparkline.map((score, i) => ({
        date: new Date(Date.now() - (sparkline.length - 1 - i) * 7 * 86400000)
          .toISOString().split('T')[0],
        score,
        mention_count: Math.floor((product?.aspects[0]?.mention_count ?? 100) / Math.max(1, sparkline.length)),
      })),
      brand: product?.brand ?? null,
      category: product?.category ?? null,
    };
  }
  return apiFetch<TimeseriesResponse>(`/api/products/${encodeURIComponent(model)}/timeseries`);
}

// --- Platform Comparison ---

export async function fetchPlatformComparison(
  brand?: Brand,
  category?: Category,
  product_model?: string
): Promise<PlatformComparisonResponse> {
  if (USE_FIXTURES) return FIXTURE_PLATFORM_COMPARISON;
  return apiFetch<PlatformComparisonResponse>('/api/platforms/comparison', { brand, category, product_model });
}

// Backwards-compat alias
export const fetchPlatformBreakdown = fetchPlatformComparison;

// --- Topic Explorer ---

export async function fetchTopicExplorer(brand?: Brand, category?: Category): Promise<TopicExplorerResponse> {
  if (USE_FIXTURES) return FIXTURE_TOPIC_EXPLORER;
  return apiFetch<TopicExplorerResponse>('/api/topics', { brand, category });
}

export async function fetchTopicComparative(
  brand_a: Brand,
  brand_b: Brand,
  category?: Category
): Promise<ComparativeTopicResponse> {
  if (USE_FIXTURES) return FIXTURE_TOPIC_COMPARATIVE;
  return apiFetch<ComparativeTopicResponse>('/api/topics/comparative', { brand_a, brand_b, category });
}

// --- Alerts ---

export async function fetchAlerts(
  acknowledged?: boolean,
  brand?: Brand,
  category?: Category,
  platforms?: SourcePlatform[]
): Promise<AlertListResponse> {
  if (USE_FIXTURES) {
    let items = FIXTURE_ALERTS.filter((a) =>
      acknowledged === undefined ? true : a.acknowledged === acknowledged
    );
    if (brand) items = items.filter((a) => a.brand === brand);
    return { total: items.length, items };
  }
  // platforms is a repeated query param: ?platforms=reddit&platforms=amazon
  const platformParams = platforms?.length
    ? Object.fromEntries(platforms.map((p, i) => [`platforms[${i}]`, p]))
    : {};
  return apiFetch<AlertListResponse>('/api/alerts', {
    acknowledged: acknowledged === undefined ? undefined : String(acknowledged),
    brand,
    category,
    ...platformParams,
  });
}

export async function fetchAlertsHistory(brand?: Brand, category?: Category): Promise<AlertListResponse> {
  return fetchAlerts(true, brand, category);
}

export async function acknowledgeAlert(alertId: string): Promise<void> {
  if (USE_FIXTURES) {
    const alert = FIXTURE_ALERTS.find((a) => a.alert_id === alertId);
    if (alert) alert.acknowledged = true;
    return;
  }
  await fetch(
    `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'}/api/alerts/${alertId}/acknowledge`,
    { method: 'PATCH' }
  );
}

// --- Mentions ---

export async function fetchMentions(params?: {
  brand?: Brand;
  category?: Category;
  platform?: SourcePlatform;
  product_model?: string;
  topic_id?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}): Promise<MentionListResponse> {
  if (USE_FIXTURES) {
    let items = FIXTURE_MENTIONS;
    if (params?.brand) items = items.filter((m) => m.brand === params.brand);
    if (params?.platform) items = items.filter((m) => m.source_platform === params.platform);
    if (params?.product_model) items = items.filter((m) => m.product_model === params.product_model);
    if (params?.topic_id) items = items.filter((m) =>
      m.derived.aspects?.some((a) => a.name === params.topic_id)
    );
    const limit = params?.limit ?? 10;
    const offset = params?.offset ?? 0;
    const page = items.slice(offset, offset + limit);
    return { total: items.length, items: page };
  }
  return apiFetch<MentionListResponse>('/api/mentions', {
    brand: params?.brand,
    category: params?.category,
    platform: params?.platform,
    product_model: params?.product_model,
    topic_id: params?.topic_id,
    date_from: params?.date_from,
    date_to: params?.date_to,
    limit: params?.limit !== undefined ? String(params.limit) : undefined,
    offset: params?.offset !== undefined ? String(params.offset) : undefined,
  });
}

// Drilldown helper — fetches up to limit mentions for EvidenceDrilldown
export async function fetchDrilldownMentions(params?: {
  brand?: Brand;
  platform?: SourcePlatform;
  product_model?: string;
  topic_id?: string;
  limit?: number;
}): Promise<Mention[]> {
  const result = await fetchMentions({ ...params, limit: params?.limit ?? 10 });
  return result.items;
}

// --- Forecast ---

// Now sourced from generated api-contract.yaml (Batch 1 regen, R4-P0-4).
export type ForecastPoint = components['schemas']['ForecastPoint'];
export type ForecastResponse = components['schemas']['ForecastResponse'];

function buildForecastFixture(model: string, mentionCount: number): ForecastResponse {
  const today = new Date();
  const historical = Array.from({ length: 8 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (7 - i) * 4);
    const baseScore = 0.35 + Math.sin(i * 0.9) * 0.18;
    return {
      date: d.toISOString().split('T')[0],
      score: parseFloat(baseScore.toFixed(3)),
      mention_count: Math.floor(mentionCount / 8),
    };
  });

  const lastScore = historical[historical.length - 1].score;
  const forecast: ForecastPoint[] = Array.from({ length: 4 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() + (i + 1) * 7);
    const projected = parseFloat((lastScore + (i + 1) * 0.02).toFixed(3));
    const bandWidth = 0.05 + i * 0.04; // widens with horizon
    return {
      date: d.toISOString().split('T')[0],
      projected_score: projected,
      confidence_lower: parseFloat((projected - bandWidth).toFixed(3)),
      confidence_upper: parseFloat((projected + bandWidth).toFixed(3)),
    };
  });

  return {
    product_model: model,
    historical,
    forecast,
    method_label: 'Exponential decay + linear projection',
    input_mention_count: mentionCount,
    input_window_days: 30,
    low_confidence: mentionCount < 50,
    caveats: [
      'Based on review-text mentions over the past 30 days.',
      'Sentiment velocity computed per aspect, then aggregated.',
      'Confidence bands widen linearly with projection horizon.',
    ],
  };
}

export async function fetchForecast(model: string): Promise<ForecastResponse> {
  if (USE_FIXTURES) {
    const product = FIXTURE_PRODUCTS.find((p) => p.product_model === model);
    const mentionCount = product?.mention_count ?? 25;
    return buildForecastFixture(model, mentionCount);
  }
  return apiFetch<ForecastResponse>(`/api/products/${encodeURIComponent(model)}/forecast`);
}

// --- Simulator ---

// Now sourced from generated api-contract.yaml (Batch 2 regen, R4-P1-2).
export type SimulatedSegment = components['schemas']['SimulatedSegment'];
export type SimulationResult = components['schemas']['SimulationResult'];
export type SimulationRequest = components['schemas']['SimulationRequest'];

// Convenience type for the polarity union (derived from generated SimulatedSegment)
export type SimulatorPolarity = SimulatedSegment['predicted_reaction'];

function buildSimulatorFixture(scenario: string, productModel: string | null): SimulationResult {
  return {
    scenario,
    product_model: productModel,
    segments: [
      {
        segment_label: 'Mainstream consumers',
        predicted_reaction: 'positive',
        confidence_narrative:
          'Budget-focused buyers frequently cite value and suction in reviews. A $99 price point would expand reach into first-time vacuum buyers who currently opt for competitors.',
        key_quotes_used: [
          "It does the job perfectly for the price — couldn't ask for more at this range.",
          'Suction is surprisingly strong for such a compact unit.',
        ],
      },
      {
        segment_label: 'Existing Shark owners',
        predicted_reaction: 'mixed',
        confidence_narrative:
          'Loyal owners express concern about brand dilution. Some welcome entry-level accessibility; others worry about quality trade-offs impacting the premium Shark reputation.',
        key_quotes_used: [
          "I've been buying Shark for years — hope they don't cut corners on a cheaper model.",
          'Would be great to recommend to my parents without breaking the bank.',
        ],
      },
      {
        segment_label: 'Renter market',
        predicted_reaction: 'positive',
        confidence_narrative:
          'Reviewers in smaller living situations consistently mention storage and portability. A dedicated renter SKU addresses unmet needs directly, with high conversion likelihood.',
        key_quotes_used: [
          'Perfect for my apartment — takes up almost no space.',
          'Wish they made one specifically for smaller homes.',
        ],
      },
    ],
    overall_disclaimer: 'Simulated reaction based on LLM heuristic, not empirical behavior modeling.',
    model_used: 'fixture-mode (backend endpoint not available)',
    tokens_consumed: 0,
  };
}

export async function postSimulate(request: SimulationRequest): Promise<SimulationResult> {
  if (USE_FIXTURES) {
    // Simulate async latency for demo realism
    await new Promise((r) => setTimeout(r, 1200));
    return buildSimulatorFixture(request.scenario, request.product_model ?? null);
  }
  const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
  const res = await fetch(`${apiBase}/api/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    signal: AbortSignal.timeout(30000),
    body: JSON.stringify(request),
  });
  // 503 = LLM API key not configured — fall back to fixture so demo still works
  if (res.status === 503) {
    await new Promise((r) => setTimeout(r, 800));
    return buildSimulatorFixture(request.scenario, request.product_model ?? null);
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<SimulationResult>;
}
