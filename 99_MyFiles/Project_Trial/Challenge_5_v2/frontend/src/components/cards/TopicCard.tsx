import type { TopicCluster } from '../../types';
import { SentimentBadge } from '../shared/SentimentBadge';

interface Props {
  topic: TopicCluster;
  onClick: () => void;
}

export function TopicCard({ topic, onClick }: Props) {
  const momentumPositive = topic.momentum > 0;
  const momentumColor = momentumPositive ? 'var(--positive)' : 'var(--negative)';
  const scoreLabel = topic.avg_score > 0.2 ? 'positive' : topic.avg_score < -0.2 ? 'negative' : 'neutral';

  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      role="button"
      tabIndex={0}
      aria-label={`Topic: ${topic.label}, ${topic.mention_count} mentions, ${scoreLabel} sentiment`}
      className="section-card hover-row"
      style={{
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        padding: '14px 16px',
        transition: 'border-color 0.12s ease-out, background 0.12s ease-out',
      }}
    >
      {/* Momentum indicator */}
      <div
        aria-hidden="true"
        style={{
          width: 36,
          height: 36,
          borderRadius: 8,
          background: momentumColor + '22',
          color: momentumColor,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 16,
          fontWeight: 700,
          flexShrink: 0,
        }}
      >
        {momentumPositive ? '↑' : '↓'}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
            {topic.label}
          </span>
          {/* NEW badge for novel clusters */}
          {topic.is_novel && (
            <span
              aria-label="Emerging topic — newly detected"
              style={{
                fontSize: 10,
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: 0.8,
                color: 'var(--positive)',
                background: 'var(--positive)22',
                border: '1px solid var(--positive)44',
                borderRadius: 999,
                padding: '2px 6px',
              }}
            >
              NEW
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <SentimentBadge label={scoreLabel} score={topic.avg_score} size="sm" />
          <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
            {topic.mention_count.toLocaleString()} mentions
          </span>
          <span style={{ fontSize: 12, color: momentumColor, fontWeight: 600 }}>
            {momentumPositive ? '+' : ''}{topic.momentum.toFixed(1)}% momentum
          </span>
        </div>
        {topic.exemplar_quotes[0] && (
          <p
            style={{
              margin: '6px 0 0',
              fontSize: 12,
              color: 'var(--text-secondary)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            "{topic.exemplar_quotes[0]}"
          </p>
        )}
      </div>

      <span style={{ fontSize: 12, color: 'var(--accent)', flexShrink: 0 }} aria-hidden="true">View →</span>
    </div>
  );
}
