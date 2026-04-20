import { useEffect, useState } from 'react';
import { useFilterStore } from '../store/filterStore';
import { useDrilldownStore } from '../store/drilldownStore';
import { fetchTopicExplorer, fetchTopicComparative } from '../api/endpoints';
import type { TopicCluster, ComparativeTopicResponse, ShareOfAspect, Brand, Category } from '../types';
import { TopicCard } from '../components/cards/TopicCard';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { COLORS } from '../theme';

const PAGE_SUBTITLE =
  'What aspects are people talking about that we did not pre-define, and are any of them gaining or losing ground?';

type SortMode = 'momentum' | 'mention_count' | 'avg_score';

export function TopicExplorerPage() {
  const { brands, categories, platforms, dateRange } = useFilterStore();
  const openDrilldown = useDrilldownStore((s) => s.openDrilldown);

  const brand = brands[0] as Brand | undefined;
  const category = categories[0] as Category | undefined;

  const [topics, setTopics] = useState<TopicCluster[]>([]);
  const [comparison, setComparison] = useState<ShareOfAspect[]>([]);
  const [sort, setSort] = useState<SortMode>('momentum');
  const [showNovelOnly, setShowNovelOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetchTopicExplorer(brand, category),
      fetchTopicComparative('shark' as Brand, 'dyson' as Brand, category),
    ]).then(([explorerResponse, comparativeResponse]: [{ topics: TopicCluster[] }, ComparativeTopicResponse]) => {
      const sorted = [...explorerResponse.topics].sort((a, b) => {
        if (sort === 'momentum') return b.momentum - a.momentum;
        if (sort === 'mention_count') return b.mention_count - a.mention_count;
        return b.avg_score - a.avg_score;
      });
      setTopics(sorted);
      setComparison(comparativeResponse.share_of_aspect);
      setLoading(false);
    }).catch(() => {
      setError('Failed to load topic data. Please try again.');
      setLoading(false);
    });
  }, [brand, category, platforms, dateRange, sort]);

  // Pivot flat share_of_aspect rows into per-aspect grouped chart data
  const aspectMap: Record<string, { Shark: number; Dyson: number }> = {};
  for (const sa of comparison) {
    if (!aspectMap[sa.aspect]) aspectMap[sa.aspect] = { Shark: 0, Dyson: 0 };
    if (sa.brand === 'shark') aspectMap[sa.aspect].Shark = sa.mention_share;
    if (sa.brand === 'dyson') aspectMap[sa.aspect].Dyson = sa.mention_share;
  }
  const comparisonChartData = Object.entries(aspectMap).map(([aspect, vals]) => ({
    topic: aspect.replace(/_/g, ' '),
    ...vals,
  }));

  // Apply novel filter if toggle is on
  const displayedTopics = showNovelOnly
    ? topics.filter((t) => t.is_novel === true)
    : topics;

  return (
    <div className="page-content">
      <div>
        <h1 className="page-title">Topic Explorer</h1>
        <p className="page-subtitle">{PAGE_SUBTITLE}</p>
      </div>

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 24 }} className="section-grid-2">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: 100, borderRadius: 'var(--radius)' }} />
            ))}
          </div>
          <div className="skeleton" style={{ height: 360, borderRadius: 'var(--radius)' }} />
        </div>
      ) : error ? (
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>Retry</button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 24 }} className="section-grid-2">
          {/* Topic list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* Sort + filter controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span className="section-label" style={{ marginRight: 4 }}>Sort by:</span>
              {(['momentum', 'mention_count', 'avg_score'] as SortMode[]).map((s) => (
                <button
                  key={s}
                  onClick={() => setSort(s)}
                  aria-pressed={sort === s}
                  className="btn"
                  style={{
                    background: sort === s ? 'var(--accent)' : 'var(--bg-surface)',
                    color: sort === s ? '#fff' : 'var(--text-secondary)',
                    border: '1px solid ' + (sort === s ? 'var(--accent)' : 'var(--border)'),
                    borderRadius: 4,
                    padding: '4px 10px',
                    fontSize: 12,
                  }}
                >
                  {s.replace(/_/g, ' ')}
                </button>
              ))}
              <button
                onClick={() => setShowNovelOnly((v) => !v)}
                aria-pressed={showNovelOnly}
                className="btn"
                style={{
                  background: showNovelOnly ? 'var(--positive)22' : 'var(--bg-surface)',
                  color: showNovelOnly ? 'var(--positive)' : 'var(--text-secondary)',
                  border: '1px solid ' + (showNovelOnly ? 'var(--positive)' : 'var(--border)'),
                  borderRadius: 4,
                  padding: '4px 10px',
                  fontSize: 12,
                  marginLeft: 8,
                }}
              >
                Show emerging only
              </button>
            </div>

            {displayedTopics.length === 0 ? (
              <div className="section-card">
                <div className="empty-state">
                  <span className="empty-state-icon" aria-hidden="true">○</span>
                  <p className="empty-state-title">No topics found</p>
                  <p className="empty-state-desc">
                    {showNovelOnly ? 'No emerging topics detected. Try removing the "Show emerging only" filter.' : 'No topics match the current filter.'}
                  </p>
                </div>
              </div>
            ) : (
              displayedTopics.map((t) => (
                <TopicCard
                  key={t.topic_id}
                  topic={t}
                  onClick={() =>
                    openDrilldown({
                      title: `Topic: ${t.label}`,
                      total_mentions: t.mention_count,
                      sentiment_score: t.avg_score,
                      filters: {},
                      aspect: t.topic_id,
                    })
                  }
                />
              ))
            )}
          </div>

          {/* Comparison panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <SectionCard title="Share of Aspect: Shark vs Dyson">
              <p style={{ margin: '0 0 12px', fontSize: 12, color: 'var(--text-secondary)' }}>
                Not share of voice — this shows how many mentions each brand gets per topic.
              </p>
              {comparisonChartData.length === 0 ? (
                <div className="empty-state" style={{ padding: '24px 0' }}>
                  <p className="empty-state-desc">No comparison data available.</p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart
                    data={comparisonChartData}
                    layout="vertical"
                    margin={{ top: 0, right: 16, left: 0, bottom: 0 }}
                    aria-label="Share of aspect comparison between Shark and Dyson"
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
                    <XAxis type="number" tick={{ fill: COLORS.textTertiary, fontSize: 11 }} />
                    <YAxis dataKey="topic" type="category" tick={{ fill: COLORS.textSecondary, fontSize: 11 }} width={130} />
                    <Tooltip
                      contentStyle={{
                        background: COLORS.bgSurfaceRaised,
                        border: `1px solid ${COLORS.border}`,
                        color: COLORS.textPrimary,
                        fontSize: 12,
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: 12, color: COLORS.textSecondary }} />
                    <Bar dataKey="Shark" fill={COLORS.accent} radius={[0, 4, 4, 0]} />
                    <Bar dataKey="Dyson" fill={COLORS.neutral} radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </SectionCard>
          </div>
        </div>
      )}
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="section-card">
      <h3 className="section-label" style={{ margin: '0 0 12px' }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
