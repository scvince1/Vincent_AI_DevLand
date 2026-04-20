import { useEffect, useState } from 'react';
import { useFilterStore } from '../store/filterStore';
import { useDrilldownStore } from '../store/drilldownStore';
import { fetchAlerts, fetchAlertsHistory, acknowledgeAlert } from '../api/endpoints';
import type { AlertEvent, Brand, Category, SourcePlatform } from '../types';
import { AlertCard } from '../components/cards/AlertCard';

const PAGE_SUBTITLE =
  'What should I be paying attention to right now that I do not already know about?';

export function AlertsInsightsPage() {
  const { brands, categories, platforms, dateRange } = useFilterStore();
  const openDrilldown = useDrilldownStore((s) => s.openDrilldown);

  const brand = brands[0] as Brand | undefined;
  const category = categories[0] as Category | undefined;

  const [activeAlerts, setActiveAlerts] = useState<AlertEvent[]>([]);
  const [history, setHistory] = useState<AlertEvent[]>([]);
  const [tab, setTab] = useState<'active' | 'history'>('active');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetchAlerts(false, brand, category, platforms.length > 0 ? (platforms as SourcePlatform[]) : undefined),
      fetchAlertsHistory(brand, category),
    ]).then(([active, hist]) => {
      setActiveAlerts([...active.items].sort((a, b) => b.severity - a.severity));
      setHistory(hist.items);
      setLoading(false);
    }).catch(() => {
      setError('Failed to load alerts. Please try again.');
      setLoading(false);
    });
  }, [brand, category, platforms, dateRange]);

  const handleAcknowledge = async (alertId: string) => {
    await acknowledgeAlert(alertId);
    setActiveAlerts((prev) => prev.filter((a) => a.alert_id !== alertId));
  };

  const handleViewEvidence = (alert: AlertEvent) => {
    openDrilldown({
      title: `${alert.aspect.replace(/_/g, ' ')} — ${alert.product_model ?? alert.brand}`,
      total_mentions: alert.exemplar_mentions?.length ?? 0,
      sentiment_score: -(alert.score_drop ?? 0.6),
      filters: { brands: [alert.brand] },
      aspect: alert.aspect,
    });
  };

  // Partition active alerts: safety recalls surface first, as a distinct section.
  const recallAlerts = activeAlerts.filter(
    (a) => (a as AlertEvent & { alert_type?: string }).alert_type === 'safety_recall'
  );
  const reviewAlerts = activeAlerts.filter(
    (a) => (a as AlertEvent & { alert_type?: string }).alert_type !== 'safety_recall'
  );

  const displayed = tab === 'active' ? reviewAlerts : history;

  return (
    <div className="page-content" style={{ maxWidth: 900 }}>
      <div>
        <h1 className="page-title">Alerts & Insights</h1>
        <p className="page-subtitle">{PAGE_SUBTITLE}</p>
      </div>

      {/* Tab bar */}
      <div role="tablist" style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--border)', paddingBottom: 0 }}>
        {(['active', 'history'] as const).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className="btn"
            style={{
              background: 'none',
              border: 'none',
              borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent',
              color: tab === t ? 'var(--text-primary)' : 'var(--text-tertiary)',
              padding: '8px 16px',
              fontSize: 14,
              fontWeight: tab === t ? 600 : 400,
              cursor: 'pointer',
              marginBottom: -1,
              borderRadius: 0,
            }}
          >
            {t === 'active'
              ? `Active Alerts (${activeAlerts.length})`
              : `History (${history.length})`}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: 120, borderRadius: 'var(--radius)' }} />
          ))}
        </div>
      ) : error ? (
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      ) : (
        <>
          {/* Safety Recalls section — always shown first when recalls exist on active tab */}
          {tab === 'active' && recallAlerts.length > 0 && (
            <section aria-label="Safety Recalls">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  marginBottom: 12,
                  paddingBottom: 8,
                  borderBottom: '1px solid var(--color-recall-badge-border)',
                }}
              >
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: 0.8,
                    color: 'var(--color-critical)',
                  }}
                >
                  Safety Recalls
                </span>
                <span
                  style={{
                    fontSize: 11,
                    color: 'var(--text-tertiary)',
                    background: 'var(--color-recall-badge-bg)',
                    border: '1px solid var(--color-recall-badge-border)',
                    borderRadius: 999,
                    padding: '1px 7px',
                  }}
                >
                  Official CPSC Notices · {recallAlerts.length}
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {recallAlerts.map((alert) => (
                  <AlertCard
                    key={alert.alert_id}
                    alert={alert}
                    onViewEvidence={() => handleViewEvidence(alert)}
                    onAcknowledge={() => handleAcknowledge(alert.alert_id)}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Standard alerts section */}
          {displayed.length === 0 ? (
            <div className="section-card">
              <div className="empty-state">
                <span className="empty-state-icon" aria-hidden="true">
                  {tab === 'active' ? '✓' : '○'}
                </span>
                <p className="empty-state-title">
                  {tab === 'active' ? 'All clear' : 'No history yet'}
                </p>
                <p className="empty-state-desc">
                  {tab === 'active'
                    ? 'No active sentiment alerts. Signals are stable.'
                    : 'Acknowledged alerts will appear here.'}
                </p>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {displayed.map((alert) => (
                <AlertCard
                  key={alert.alert_id}
                  alert={alert}
                  onViewEvidence={() => handleViewEvidence(alert)}
                  onAcknowledge={() => handleAcknowledge(alert.alert_id)}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
