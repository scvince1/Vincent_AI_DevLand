import type { AlertEvent } from '../../types';
import { SeverityBar } from '../shared/SeverityBar';

interface Props {
  alert: AlertEvent;
  onViewEvidence: () => void;
  onAcknowledge: () => void;
}

/**
 * Safety Recall badge — renders when alert.alert_type === 'safety_recall'.
 * Authoritative-government styling: red, uppercase, official-source framing.
 */
function SafetyRecallBadge() {
  return (
    <span
      aria-label="Safety Recall — official CPSC notice"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        fontSize: 11,
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: 0.8,
        color: 'var(--color-critical)',
        background: 'var(--color-recall-badge-bg)',
        border: '1px solid var(--color-recall-badge-border)',
        borderRadius: 'var(--radius-sm)',
        padding: '2px 8px',
      }}
    >
      <span aria-hidden="true" style={{ fontSize: 10 }}>&#9888;</span>
      Safety Recall
    </span>
  );
}

export function AlertCard({ alert, onViewEvidence, onAcknowledge }: Props) {
  // Determine if this is a safety recall alert (R4-P0-3).
  // alert_type field arrives after backend-v4 contract update.
  // Cast to access the field — it will be type-safe once gen:types is run.
  const isRecall = (alert as AlertEvent & { alert_type?: string }).alert_type === 'safety_recall';

  // R4-P0-4: use first-class `platforms` field (now a proper schema field after Batch 1 regen).
  // Fall back to derivation from exemplar_mentions if field is absent or empty.
  const contributingPlatforms: string[] =
    alert.platforms && alert.platforms.length > 0
      ? alert.platforms
      : alert.exemplar_mentions
      ? [...new Set(alert.exemplar_mentions.map((m) => m.source_platform))]
      : [];

  // Safety recalls always render at max visual severity (override computed color)
  const severityColor = isRecall
    ? 'var(--color-critical)'
    : alert.severity >= 0.75
    ? 'var(--severity-high)'
    : alert.severity >= 0.5
    ? 'var(--severity-medium)'
    : 'var(--severity-low)';

  const borderColor = isRecall
    ? 'var(--color-recall-badge-border)'
    : alert.severity >= 0.75
    ? 'var(--severity-high)'
    : 'var(--border)';

  const ago = getTimeAgo(alert.triggered_at);
  const exemplarCount = alert.exemplar_mentions?.length ?? 0;
  const previewQuote = alert.exemplar_mentions?.[0]?.text;

  // CPSC source URL — present on recall alerts (R4-P0-3 contract addition)
  const cpscUrl = (alert as AlertEvent & { source_url?: string }).source_url;

  return (
    <div
      className="section-card"
      style={{
        border: `1px solid ${borderColor}`,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        transition: 'border-color 0.12s ease-out',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        {isRecall ? (
          <SafetyRecallBadge />
        ) : (
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: 1,
              color: severityColor,
            }}
          >
            Severity {(alert.severity * 100).toFixed(0)}
          </span>
        )}

        {/* Platform confirmation chip — requires 2+ platforms (v3 decision preserved) */}
        {contributingPlatforms.length > 1 && (
          <span
            aria-label={`Cross-platform confirmation: ${contributingPlatforms.join(', ')}`}
            style={{
              fontSize: 11,
              color: 'var(--text-tertiary)',
              background: 'var(--bg-surface-raised)',
              border: '1px solid var(--border)',
              borderRadius: 999,
              padding: '2px 8px',
            }}
          >
            {contributingPlatforms.join(' + ')}
          </span>
        )}

        <span style={{ fontSize: 12, color: 'var(--text-tertiary)', marginLeft: 'auto' }}>{ago}</span>
      </div>

      {/* Description — recall alerts have different framing */}
      <div>
        {isRecall ? (
          <>
            <span style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 600 }}>
              {alert.aspect.replace(/_/g, ' ')}
            </span>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
              {alert.brand} · Official CPSC Safety Notice
            </p>
          </>
        ) : (
          <>
            <span style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 600 }}>
              {alert.aspect.replace(/_/g, ' ')} sentiment dropped {Math.abs(alert.score_drop * 100).toFixed(1)}%
            </span>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
              {alert.brand} · {alert.product_model ?? 'All models'}
            </p>
          </>
        )}
      </div>

      {/* Preview quote (reviews only) */}
      {!isRecall && previewQuote && (
        <blockquote
          style={{
            margin: 0,
            borderLeft: '3px solid var(--negative)',
            paddingLeft: 10,
            fontSize: 12,
            color: 'var(--text-secondary)',
            fontStyle: 'italic',
            lineHeight: 1.5,
          }}
        >
          "{previewQuote.slice(0, 140)}{previewQuote.length > 140 ? '...' : ''}"
        </blockquote>
      )}

      {/* Recall: show description text from exemplar if available */}
      {isRecall && previewQuote && (
        <p style={{ margin: 0, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          {previewQuote.slice(0, 220)}{previewQuote.length > 220 ? '...' : ''}
        </p>
      )}

      {/* Severity bar */}
      <SeverityBar score={alert.severity} />

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {isRecall && cpscUrl ? (
          <a
            href={cpscUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
            aria-label="View this recall on CPSC.gov"
            style={{ textDecoration: 'none' }}
          >
            View on CPSC.gov &#8599;
          </a>
        ) : (
          <button
            onClick={onViewEvidence}
            className="btn btn-primary"
            aria-label={`View ${exemplarCount > 0 ? exemplarCount + ' ' : ''}mentions for ${alert.aspect.replace(/_/g, ' ')}`}
          >
            View {exemplarCount > 0 ? `${exemplarCount} ` : ''}mentions
          </button>
        )}
        {!alert.acknowledged && (
          <button
            onClick={onAcknowledge}
            className="btn btn-ghost"
            aria-label={`Acknowledge alert for ${alert.aspect.replace(/_/g, ' ')}`}
          >
            Acknowledge
          </button>
        )}
      </div>
    </div>
  );
}

function getTimeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diffMs / 3600000);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}
