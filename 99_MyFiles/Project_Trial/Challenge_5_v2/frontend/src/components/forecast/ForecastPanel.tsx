import {
  ComposedChart,
  Line,
  Area,
  ReferenceLine,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useState } from 'react';
import { LowConfidenceBadge } from './LowConfidenceBadge';
import type { ForecastPoint, ForecastResponse, TimeseriesPoint } from '../../api/endpoints';

// ─── Chart data shape ─────────────────────────────────────────────────────────

interface ChartPoint {
  date: string;
  /** Historical actual score — null on forecast-only points */
  actual: number | null;
  /** Forecast projected score — null on historical-only points */
  projected: number | null;
  /** Confidence upper bound — null on historical points */
  upper: number | null;
  /** Confidence lower bound — null on historical points */
  lower: number | null;
  isForecast: boolean;
}

function buildChartData(
  historical: TimeseriesPoint[],
  forecast: ForecastPoint[]
): ChartPoint[] {
  const historicalPoints: ChartPoint[] = historical.map((h) => ({
    date: h.date,
    actual: h.score,
    projected: null,
    upper: null,
    lower: null,
    isForecast: false,
  }));

  // The join point — last historical point is shared as first forecast point
  // so the visual transition is seamless.
  const joinDate = historical.length > 0 ? historical[historical.length - 1].date : null;

  const forecastPoints: ChartPoint[] = forecast.map((f) => ({
    date: f.date,
    actual: f.date === joinDate ? historical[historical.length - 1].score : null,
    projected: f.projected_score,
    upper: f.confidence_upper,
    lower: f.confidence_lower,
    isForecast: true,
  }));

  return [...historicalPoints, ...forecastPoints];
}

function todayIndex(data: ChartPoint[]): string | undefined {
  // "Today" marker — find last non-forecast point date
  const last = data.filter((d) => !d.isForecast).at(-1);
  return last?.date;
}

// ─── Caveat tooltip ────────────────────────────────────────────────────────────

function CaveatIcon({ caveats }: { caveats: string[] }) {
  const [open, setOpen] = useState(false);

  return (
    <span style={{ position: 'relative', display: 'inline-block' }}>
      <button
        aria-label="View forecast caveats"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        onBlur={() => setOpen(false)}
        className="btn"
        style={{
          background: 'none',
          border: 'none',
          padding: '0 2px',
          fontSize: 12,
          color: 'var(--text-tertiary)',
          cursor: 'pointer',
          lineHeight: 1,
        }}
      >
        (i)
      </button>
      {open && caveats.length > 0 && (
        <div
          role="tooltip"
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            zIndex: 10,
            background: 'var(--bg-surface-raised)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '10px 14px',
            minWidth: 240,
            maxWidth: 320,
            boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
          }}
        >
          <ul style={{ margin: 0, padding: '0 0 0 14px', fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {caveats.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}
    </span>
  );
}

// ─── Custom tooltip ────────────────────────────────────────────────────────────

function ForecastTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  const pointMap: Record<string, number> = {};
  for (const p of payload) {
    if (p.value !== null && p.value !== undefined) pointMap[p.name] = p.value;
  }
  return (
    <div
      style={{
        background: 'var(--bg-surface-raised)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        padding: '8px 12px',
        fontSize: 12,
        color: 'var(--text-primary)',
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      {pointMap['actual'] !== undefined && (
        <div>Actual: <span style={{ color: 'var(--chart-blue)' }}>{(pointMap['actual'] * 100).toFixed(1)}%</span></div>
      )}
      {pointMap['projected'] !== undefined && (
        <div>Projected: <span style={{ color: 'var(--chart-blue)' }}>{(pointMap['projected'] * 100).toFixed(1)}%</span></div>
      )}
      {pointMap['upper'] !== undefined && pointMap['lower'] !== undefined && (
        <div style={{ color: 'var(--text-tertiary)' }}>
          Range: {(pointMap['lower'] * 100).toFixed(1)}% &ndash; {(pointMap['upper'] * 100).toFixed(1)}%
        </div>
      )}
    </div>
  );
}

// ─── Main component ────────────────────────────────────────────────────────────

interface ForecastPanelProps {
  data: ForecastResponse | null;
  loading?: boolean;
  error?: string | null;
}

export function ForecastPanel({ data, loading, error }: ForecastPanelProps) {
  if (loading) {
    return (
      <div className="section-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
          <div className="skeleton skeleton-title" style={{ width: 140 }} />
          <div className="skeleton skeleton-text" style={{ width: 180 }} />
        </div>
        <div className="skeleton" style={{ height: 240, borderRadius: 'var(--radius)' }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="section-card">
        <h3 className="section-label" style={{ margin: '0 0 12px' }}>Trend Forecast</h3>
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.forecast.length === 0) {
    return (
      <div className="section-card">
        <h3 className="section-label" style={{ margin: '0 0 12px' }}>Trend Forecast</h3>
        <div className="empty-state">
          <span className="empty-state-icon" aria-hidden="true">○</span>
          <p className="empty-state-title">No forecast data</p>
          <p className="empty-state-desc">Insufficient data to generate a forecast for this product.</p>
        </div>
      </div>
    );
  }

  const chartData = buildChartData(data.historical, data.forecast);
  const today = todayIndex(chartData);
  const lowConfidence = data.low_confidence;
  const forecastOpacity = lowConfidence ? 0.4 : 1;

  return (
    <div className="section-card">
      {/* Card header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <h3 className="section-label" style={{ margin: 0 }}>Trend Forecast</h3>
          <CaveatIcon caveats={data.caveats} />
        </div>
        <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
          {data.method_label} &middot; {data.input_mention_count} mentions over {data.input_window_days} days
        </span>
        {lowConfidence && (
          <LowConfidenceBadge
            mentionCount={data.input_mention_count}
            windowDays={data.input_window_days}
          />
        )}
      </div>

      {/* Recharts ComposedChart */}
      <ResponsiveContainer width="100%" height={240}>
        <ComposedChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[-1, 1]}
            tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
            axisLine={false}
            tickLine={false}
            width={42}
          />
          <Tooltip content={<ForecastTooltip />} />

          {/* Confidence band — rendered below forecast line */}
          <Area
            dataKey="upper"
            name="upper"
            fill="var(--chart-blue)"
            fillOpacity={0.15}
            stroke="none"
            activeDot={false}
            isAnimationActive={false}
          />
          <Area
            dataKey="lower"
            name="lower"
            fill="var(--bg-base)"
            fillOpacity={1}
            stroke="none"
            activeDot={false}
            isAnimationActive={false}
          />

          {/* Historical (actual) line — solid, weight 2 */}
          <Line
            dataKey="actual"
            name="actual"
            stroke="var(--chart-blue)"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />

          {/* Forecast dashed line — starts at join point */}
          <Line
            dataKey="projected"
            name="projected"
            stroke="var(--chart-blue)"
            strokeWidth={1.5}
            strokeDasharray="6 4"
            strokeOpacity={forecastOpacity}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />

          {/* Today marker */}
          {today && (
            <ReferenceLine
              x={today}
              stroke="var(--text-tertiary)"
              strokeDasharray="3 3"
              label={{
                value: 'Today',
                position: 'insideTopRight',
                fontSize: 10,
                fill: 'var(--text-tertiary)',
              }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Below-chart footnote — italic, 12px, text-tertiary */}
      <p
        style={{
          margin: '10px 0 0',
          fontSize: 12,
          fontStyle: 'italic',
          color: 'var(--text-tertiary)',
          lineHeight: 1.5,
        }}
      >
        Projections are model-generated estimates based on observed trends. Not a guarantee of future outcomes.
      </p>
    </div>
  );
}
