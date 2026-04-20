import { useEffect, useState } from 'react';
import { useFilterStore } from '../store/filterStore';
import { useDrilldownStore } from '../store/drilldownStore';
import { fetchProducts, fetchProductAspects, fetchProductTimeseries, fetchForecast } from '../api/endpoints';
import type { ForecastResponse } from '../api/endpoints';
import type { ProductSummary, ProductAspectResponse, AspectTrend, Brand, Category } from '../types';
import { SeverityBar } from '../components/shared/SeverityBar';
import { AspectRadarChart } from '../components/charts/AspectRadarChart';
import { SentimentLineChart } from '../components/charts/SentimentLineChart';
import { ForecastPanel } from '../components/forecast/ForecastPanel';
import { SimulatorPanel } from '../components/simulator/SimulatorPanel';

const PAGE_SUBTITLE =
  'For a specific SKU, what are people saying about each aspect of the product, and how is each aspect trending?';

function scoreLabel(s: number): string {
  return s > 0.2 ? 'positive' : s < -0.2 ? 'negative' : 'neutral';
}

export function ProductAnalysisPage() {
  const { brands, categories, platforms, dateRange, setProductModel } = useFilterStore();
  const openDrilldown = useDrilldownStore((s) => s.openDrilldown);

  const brand = brands[0] as Brand | undefined;
  const category = categories[0] as Category | undefined;

  const [products, setProducts] = useState<ProductSummary[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [productAspects, setProductAspects] = useState<ProductAspectResponse | null>(null);
  const [timeseriesData, setTimeseriesData] = useState<{ date: string; score: number; mention_count: number }[]>([]);
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [forecastError, setForecastError] = useState<string | null>(null);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load product list — re-fetches on every filter change
  useEffect(() => {
    setLoadingProducts(true);
    setError(null);
    fetchProducts(brand, category).then((list) => {
      setProducts(list);
      if (list.length > 0) {
        setSelectedModel(list[0].product_model);
      }
      setLoadingProducts(false);
    }).catch(() => {
      setError('Failed to load products.');
      setLoadingProducts(false);
    });
  }, [brand, category, platforms, dateRange]);

  // Load selected product aspects + timeseries — re-fetches on filter or model change
  useEffect(() => {
    if (!selectedModel) return;
    setLoadingDetail(true);
    setProductModel(selectedModel);
    Promise.all([
      fetchProductAspects(selectedModel),
      fetchProductTimeseries(selectedModel),
    ]).then(([p, ts]) => {
      setProductAspects(p);
      setTimeseriesData(ts.series);
      setLoadingDetail(false);
    }).catch(() => {
      setLoadingDetail(false);
    });
  }, [selectedModel, brand, category, platforms, dateRange]);

  // Load forecast — separate effect so chart loads independently of aspect data
  useEffect(() => {
    if (!selectedModel) return;
    setLoadingForecast(true);
    setForecastError(null);
    fetchForecast(selectedModel)
      .then((f) => {
        setForecastData(f);
        setLoadingForecast(false);
      })
      .catch(() => {
        setForecastError('Could not load forecast data.');
        setLoadingForecast(false);
      });
  }, [selectedModel, brand, category, platforms, dateRange]);

  const selectedProductSummary = products.find((p) => p.product_model === selectedModel);

  if (error) {
    return (
      <div className="page-content">
        <PageHeader />
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-content">
      <PageHeader />

      {/* Product selector */}
      <div className="section-card" style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span className="section-label">Select Product</span>
        {loadingProducts ? (
          <div className="skeleton skeleton-text" style={{ width: 220 }} />
        ) : products.length === 0 ? (
          <span style={{ fontSize: 13, color: 'var(--text-tertiary)' }}>No products for the current filter</span>
        ) : (
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            aria-label="Select product model"
            style={{
              background: 'var(--bg-surface-raised)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border)',
              borderRadius: 4,
              padding: '6px 12px',
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            {products.map((p) => (
              <option key={p.product_model} value={p.product_model}>
                {p.brand.toUpperCase()} — {p.product_model} ({p.mention_count.toLocaleString()} mentions, score: {(p.overall_score * 100).toFixed(0)}%)
              </option>
            ))}
          </select>
        )}
        {selectedProductSummary && (
          <span
            style={{
              fontSize: 12,
              fontWeight: 600,
              padding: '3px 8px',
              borderRadius: 4,
              background:
                selectedProductSummary.overall_score > 0.2
                  ? 'var(--positive)22'
                  : selectedProductSummary.overall_score < -0.2
                  ? 'var(--negative)22'
                  : 'var(--neutral)22',
              color:
                selectedProductSummary.overall_score > 0.2
                  ? 'var(--positive)'
                  : selectedProductSummary.overall_score < -0.2
                  ? 'var(--negative)'
                  : 'var(--neutral)',
            }}
          >
            {scoreLabel(selectedProductSummary.overall_score)} ({(selectedProductSummary.overall_score * 100).toFixed(0)}%)
          </span>
        )}
      </div>

      {loadingDetail ? (
        <>
          <div className="section-grid-2" style={{ gridTemplateColumns: '1fr 360px' }}>
            <div className="skeleton" style={{ height: 280, borderRadius: 'var(--radius)' }} />
            <div className="skeleton" style={{ height: 280, borderRadius: 'var(--radius)' }} />
          </div>
          <div className="skeleton" style={{ height: 240, borderRadius: 'var(--radius)' }} />
        </>
      ) : productAspects ? (
        <>
          {/* Aspect table + radar side by side */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 20 }} className="section-grid-2">
            <SectionCard title="Aspect Breakdown — click any row for evidence">
              <div className="table-scroll">
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, minWidth: 480 }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      {['Aspect', 'Mentions', 'Avg Score', 'Trend (30d)', 'Severity'].map((h) => (
                        <th
                          key={h}
                          scope="col"
                          style={{
                            textAlign: 'left',
                            padding: '8px 10px',
                            color: 'var(--text-tertiary)',
                            fontWeight: 600,
                            fontSize: 11,
                            textTransform: 'uppercase',
                            letterSpacing: 0.5,
                          }}
                        >
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {productAspects.aspects.length === 0 ? (
                      <tr>
                        <td colSpan={5}>
                          <div className="empty-state" style={{ padding: '24px 0' }}>
                            <p className="empty-state-desc">No aspect data for this product.</p>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      productAspects.aspects.map((a) => (
                        <AspectRow
                          key={a.aspect}
                          aspect={a}
                          onClickEvidence={() =>
                            openDrilldown({
                              title: `${a.aspect.replace(/_/g, ' ')} — ${productAspects.product_model}`,
                              total_mentions: a.mention_count,
                              sentiment_score: a.avg_score,
                              filters: { productModel: productAspects.product_model },
                              aspect: a.aspect,
                            })
                          }
                        />
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </SectionCard>

            <SectionCard title="Aspect Radar">
              <AspectRadarChart aspects={productAspects.aspects} height={280} />
            </SectionCard>
          </div>

          {/* Sentiment timeseries */}
          <SectionCard title={`Sentiment Over Time — ${productAspects.product_model}`}>
            {timeseriesData.length === 0 ? (
              <div className="empty-state" style={{ padding: '24px 0' }}>
                <p className="empty-state-desc">No timeseries data available.</p>
              </div>
            ) : (
              <SentimentLineChart data={timeseriesData} height={220} />
            )}
          </SectionCard>

          {/* Trend Forecast panel */}
          <ForecastPanel
            data={forecastData}
            loading={loadingForecast}
            error={forecastError}
          />

          {/* What-If Simulator panel */}
          <SimulatorPanel
            productModel={selectedModel || null}
            inputMentionCount={selectedProductSummary?.mention_count}
          />
        </>
      ) : selectedModel ? (
        <div className="section-card">
          <div className="empty-state">
            <span className="empty-state-icon" aria-hidden="true">○</span>
            <p className="empty-state-title">No data available</p>
            <p className="empty-state-desc">No aspect data found for this product with the current filters.</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function AspectRow({
  aspect,
  onClickEvidence,
}: {
  aspect: AspectTrend;
  onClickEvidence: () => void;
}) {
  const label = scoreLabel(aspect.avg_score);
  const color = label === 'positive' ? 'var(--positive)' : label === 'negative' ? 'var(--negative)' : 'var(--neutral)';

  return (
    <tr
      onClick={onClickEvidence}
      onKeyDown={(e) => e.key === 'Enter' && onClickEvidence()}
      tabIndex={0}
      role="button"
      aria-label={`${aspect.aspect.replace(/_/g, ' ')} — ${aspect.mention_count} mentions, score ${(aspect.avg_score * 100).toFixed(0)}%`}
      className="hover-row"
      style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }}
    >
      <td style={{ padding: '10px', color: 'var(--text-primary)', fontWeight: 500 }}>
        {aspect.aspect.replace(/_/g, ' ')}
      </td>
      <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>
        {aspect.mention_count.toLocaleString()}
      </td>
      <td style={{ padding: '10px' }}>
        <span style={{ color, fontWeight: 600, fontSize: 13 }}>
          {(aspect.avg_score * 100).toFixed(0)}%
        </span>
      </td>
      <td style={{ padding: '10px', width: 80 }}>
        <div
          aria-hidden="true"
          style={{
            height: 24,
            background: `linear-gradient(90deg, transparent, ${color}33)`,
            borderRadius: 3,
          }}
        />
      </td>
      <td style={{ padding: '10px', width: 140 }}>
        <SeverityBar score={aspect.severity} />
      </td>
    </tr>
  );
}

function PageHeader() {
  return (
    <div>
      <h1 className="page-title">Product Analysis</h1>
      <p className="page-subtitle">{PAGE_SUBTITLE}</p>
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="section-card">
      <h3 className="section-label" style={{ margin: '0 0 14px' }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
