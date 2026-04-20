import { useEffect, useState } from 'react';
import { useFilterStore } from '../store/filterStore';
import { useDrilldownStore } from '../store/drilldownStore';
import {
  fetchKpiSummary,
  fetchSentimentTimeseries,
  fetchShareOfVoice,
} from '../api/endpoints';
import type { OverviewKPIs, TimeseriesResponse, ShareOfVoiceResponse, Brand, Category } from '../types';
import { KpiCard } from '../components/cards/KpiCard';
import { SentimentLineChart } from '../components/charts/SentimentLineChart';
import { ShareOfVoiceDonut } from '../components/charts/ShareOfVoiceDonut';

const PAGE_TITLE = 'Overview';
const PAGE_SUBTITLE =
  'What is the state of consumer sentiment across our portfolio right now, and what changed this week?';

export function OverviewPage() {
  const { brands, categories, platforms, dateRange } = useFilterStore();
  const openDrilldown = useDrilldownStore((s) => s.openDrilldown);

  const brand = brands[0] as Brand | undefined;
  const category = categories[0] as Category | undefined;

  const [kpi, setKpi] = useState<OverviewKPIs | null>(null);
  const [timeseries, setTimeseries] = useState<TimeseriesResponse | null>(null);
  const [shareOfVoice, setShareOfVoice] = useState<ShareOfVoiceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetchKpiSummary(brand, category),
      fetchSentimentTimeseries(brand, category),
      fetchShareOfVoice(category),
    ]).then(([k, ts, sov]) => {
      setKpi(k);
      setTimeseries(ts);
      setShareOfVoice(sov);
      setLoading(false);
    }).catch(() => {
      setError('Failed to load overview data. Please try again.');
      setLoading(false);
    });
  }, [brand, category, platforms, dateRange]);

  if (error) {
    return (
      <div className="page-content">
        <PageHeader title={PAGE_TITLE} subtitle={PAGE_SUBTITLE} />
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading || !kpi) {
    return (
      <div className="page-content">
        <PageHeader title={PAGE_TITLE} subtitle={PAGE_SUBTITLE} />
        <div className="kpi-grid">
          {[1, 2, 3].map((i) => <div key={i} className="skeleton skeleton-card" style={{ flex: '1 1 200px' }} />)}
        </div>
        <div className="section-grid-2">
          <div className="skeleton skeleton-block" style={{ height: 320 }} />
          <div className="skeleton skeleton-block" style={{ height: 280 }} />
        </div>
        <div className="section-grid-equal">
          <div className="skeleton skeleton-block" style={{ height: 180 }} />
          <div className="skeleton skeleton-block" style={{ height: 180 }} />
        </div>
      </div>
    );
  }

  const scoreLabel = kpi.overall_score > 0.2 ? 'positive' : kpi.overall_score < -0.2 ? 'negative' : 'neutral';

  return (
    <div className="page-content">
      <PageHeader title={PAGE_TITLE} subtitle={PAGE_SUBTITLE} />

      {/* KPI strip */}
      <div className="kpi-grid">
        <KpiCard
          title="Total Mentions"
          value={kpi.total_mentions.toLocaleString()}
          subtitle="Across all platforms"
          onClick={() =>
            openDrilldown({
              title: 'All mentions',
              total_mentions: kpi.total_mentions,
              sentiment_score: kpi.overall_score,
              filters: {},
            })
          }
        />
        <KpiCard
          title="Overall Sentiment"
          value={`${(kpi.overall_score * 100).toFixed(0)}%`}
          subtitle={scoreLabel}
          delta={kpi.wow_delta}
          onClick={() =>
            openDrilldown({
              title: 'Overall sentiment — all mentions',
              total_mentions: kpi.total_mentions,
              sentiment_score: kpi.overall_score,
              filters: {},
            })
          }
        />
        <KpiCard
          title="Week-over-Week"
          value={`${kpi.wow_delta > 0 ? '+' : ''}${(kpi.wow_delta * 100).toFixed(1)}%`}
          subtitle="Sentiment delta"
          delta={kpi.wow_delta}
        />
      </div>

      {/* Main chart + share of voice */}
      <div className="section-grid-2">
        <Section title="Sentiment Over Time">
          <SentimentLineChart data={timeseries?.series ?? []} height={280} />
        </Section>

        <Section title="Share of Voice">
          <ShareOfVoiceDonut data={shareOfVoice?.brands ?? []} height={220} />
        </Section>
      </div>

      {/* Trending aspects */}
      <div className="section-grid-equal">
        <Section title="Rising Positive Aspects">
          {kpi.top_rising_positive.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <span className="empty-state-icon">+</span>
              <p className="empty-state-desc">No rising positive aspects in this window.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {kpi.top_rising_positive.map((aspect) => (
                <TrendingRow
                  key={aspect}
                  aspect={aspect}
                  direction="rising"
                  onDrilldown={() =>
                    openDrilldown({
                      title: `${aspect.replace(/_/g, ' ')} — trending positive`,
                      total_mentions: 0,
                      sentiment_score: 0.6,
                      filters: {},
                      aspect,
                    })
                  }
                />
              ))}
            </div>
          )}
        </Section>

        <Section title="Rising Negative Aspects">
          {kpi.top_rising_negative.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <span className="empty-state-icon">-</span>
              <p className="empty-state-desc">No rising negative aspects in this window.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {kpi.top_rising_negative.map((aspect) => (
                <TrendingRow
                  key={aspect}
                  aspect={aspect}
                  direction="falling"
                  onDrilldown={() =>
                    openDrilldown({
                      title: `${aspect.replace(/_/g, ' ')} — trending negative`,
                      total_mentions: 0,
                      sentiment_score: -0.6,
                      filters: {},
                      aspect,
                    })
                  }
                />
              ))}
            </div>
          )}
        </Section>
      </div>
    </div>
  );
}

function TrendingRow({
  aspect,
  direction,
  onDrilldown,
}: {
  aspect: string;
  direction: 'rising' | 'falling';
  onDrilldown: () => void;
}) {
  const isRising = direction === 'rising';
  const color = isRising ? 'var(--positive)' : 'var(--negative)';

  return (
    <div
      onClick={onDrilldown}
      onKeyDown={(e) => e.key === 'Enter' && onDrilldown()}
      role="button"
      tabIndex={0}
      aria-label={`${aspect.replace(/_/g, ' ')} — ${direction === 'rising' ? 'positive trend' : 'negative trend'}`}
      className="hover-row"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '10px 14px',
        background: 'var(--bg-surface-raised)',
        borderRadius: 'var(--radius-sm)',
        cursor: 'pointer',
        border: '1px solid transparent',
        transition: 'border-color 0.12s ease-out',
      }}
    >
      <span style={{ fontSize: 16, color }} aria-hidden="true">{isRising ? '↑' : '↓'}</span>
      <span style={{ flex: 1, fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>
        {aspect.replace(/_/g, ' ')}
      </span>
      <span style={{ fontSize: 12, color, fontWeight: 600 }}>
        {isRising ? 'positive trend' : 'negative trend'}
      </span>
    </div>
  );
}

function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div>
      <h1 className="page-title">{title}</h1>
      <p className="page-subtitle">{subtitle}</p>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="section-card">
      <h3 className="section-label" style={{ margin: '0 0 16px' }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
