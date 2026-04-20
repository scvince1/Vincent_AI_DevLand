import { useEffect, useState } from 'react';
import { useFilterStore } from '../store/filterStore';
import { useDrilldownStore } from '../store/drilldownStore';
import { fetchPlatformComparison } from '../api/endpoints';
import type { PlatformComparisonResponse, SourcePlatform, Brand, Category } from '../types';
import { PlatformHeatmap } from '../components/charts/PlatformHeatmap';

const PAGE_SUBTITLE =
  'How does the conversation about this product differ across Reddit vs Amazon vs YouTube vs Trustpilot, and are the aspects the same?';

export function PlatformComparisonPage() {
  const { brands, categories, platforms, dateRange, productModel } = useFilterStore();
  const openDrilldown = useDrilldownStore((s) => s.openDrilldown);

  const brand = brands[0] as Brand | undefined;
  const category = categories[0] as Category | undefined;

  const [data, setData] = useState<PlatformComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<SourcePlatform | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchPlatformComparison(brand, category, productModel).then((d) => {
      setData(d);
      setLoading(false);
    }).catch(() => {
      setError('Failed to load platform data. Please try again.');
      setLoading(false);
    });
  }, [brand, category, platforms, dateRange, productModel]);

  // Derive unique platforms from the grid
  const platformList = data
    ? [...new Set(data.grid.map((cell) => cell.platform))] as SourcePlatform[]
    : [];

  const activePlatform = selectedPlatform ?? platformList[0] ?? null;
  const topTopics = activePlatform && data ? data.top_topics_by_platform[activePlatform] ?? [] : [];

  // Platform mention totals from grid
  const platformMentions = data
    ? platformList.reduce<Record<string, number>>((acc, p) => {
        acc[p] = data.grid
          .filter((c) => c.platform === p)
          .reduce((sum, c) => sum + c.mention_count, 0);
        return acc;
      }, {})
    : {};

  return (
    <div className="page-content">
      <div>
        <h1 className="page-title">Platform Comparison</h1>
        <p className="page-subtitle">{PAGE_SUBTITLE}</p>
      </div>

      {loading ? (
        <>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton" style={{ height: 80, flex: '1 1 140px', borderRadius: 'var(--radius)' }} />
            ))}
          </div>
          <div className="skeleton" style={{ height: 320, borderRadius: 'var(--radius)' }} />
        </>
      ) : error ? (
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>Retry</button>
        </div>
      ) : !data || platformList.length === 0 ? (
        <div className="section-card">
          <div className="empty-state">
            <span className="empty-state-icon" aria-hidden="true">◆</span>
            <p className="empty-state-title">No platform data</p>
            <p className="empty-state-desc">No cross-platform data available for the current filters.</p>
          </div>
        </div>
      ) : (
        <>
          {/* Platform summary cards */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {platformList.map((p) => (
              <button
                key={p}
                onClick={() => setSelectedPlatform(p)}
                aria-pressed={activePlatform === p}
                aria-label={`${p}: ${(platformMentions[p] ?? 0).toLocaleString()} mentions`}
                className="btn"
                style={{
                  background: activePlatform === p ? 'var(--accent)22' : 'var(--bg-surface)',
                  border: `1px solid ${activePlatform === p ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 'var(--radius)',
                  padding: '12px 16px',
                  cursor: 'pointer',
                  minWidth: 140,
                  textAlign: 'left',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  gap: 4,
                  transition: 'background 0.12s ease-out, border-color 0.12s ease-out',
                }}
              >
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize', display: 'block' }}>
                  {p}
                </span>
                <span className="kpi-number" style={{ fontSize: 20, display: 'block' }}>
                  {(platformMentions[p] ?? 0).toLocaleString()}
                </span>
                <span className="section-label" style={{ display: 'block' }}>total mentions</span>
              </button>
            ))}
          </div>

          {/* Heatmap — horizontally scrollable on mobile */}
          <SectionCard title="Platform x Aspect Sentiment Heatmap — click any cell for evidence">
            <div className="heatmap-scroll">
              <PlatformHeatmap
                data={data}
                onCellClick={(platform, aspect, score, count) =>
                  openDrilldown({
                    title: `${platform} — ${aspect.replace(/_/g, ' ')}`,
                    total_mentions: count,
                    sentiment_score: score,
                    filters: { platforms: [platform] },
                    aspect,
                  })
                }
              />
            </div>
          </SectionCard>

          {/* Top topics for selected platform */}
          {activePlatform && topTopics.length > 0 && (
            <SectionCard title={`Top Topics on ${activePlatform}`}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {topTopics.map((topic, i) => (
                  <div
                    key={topic}
                    className="hover-row"
                    role="button"
                    tabIndex={0}
                    aria-label={`#${i + 1} ${topic.replace(/_/g, ' ')}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      padding: '8px 12px',
                      background: 'var(--bg-surface-raised)',
                      borderRadius: 'var(--radius-sm)',
                      cursor: 'pointer',
                    }}
                    onClick={() =>
                      openDrilldown({
                        title: `${activePlatform} — ${topic.replace(/_/g, ' ')}`,
                        total_mentions: 0,
                        sentiment_score: 0,
                        filters: { platforms: [activePlatform] },
                        aspect: topic,
                      })
                    }
                    onKeyDown={(e) =>
                      e.key === 'Enter' &&
                      openDrilldown({
                        title: `${activePlatform} — ${topic.replace(/_/g, ' ')}`,
                        total_mentions: 0,
                        sentiment_score: 0,
                        filters: { platforms: [activePlatform] },
                        aspect: topic,
                      })
                    }
                  >
                    <span style={{ fontSize: 12, color: 'var(--text-tertiary)', width: 20 }}>#{i + 1}</span>
                    <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>
                      {topic.replace(/_/g, ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </SectionCard>
          )}
        </>
      )}
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="section-card">
      <h3 className="section-label" style={{ margin: '0 0 16px' }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
