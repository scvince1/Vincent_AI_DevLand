import type { Mention } from '../../types';
import { SentimentBadge } from './SentimentBadge';

const PLATFORM_COLORS: Record<string, string> = {
  reddit: '#ff4500',
  amazon: '#ff9900',
  youtube: '#ff0000',
  trustpilot: '#00b67a',
  twitter: '#1d9bf0',
  other: '#8b96ab',
};

interface Props {
  mention: Mention;
}

export function MentionQuote({ mention }: Props) {
  const { derived, source_platform, posted_at, author_handle, text, rating, source_url, product_model } = mention;
  const platformColor = PLATFORM_COLORS[source_platform] ?? '#8b96ab';
  const date = new Date(posted_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  return (
    <div
      style={{
        background: 'var(--bg-surface-raised)',
        border: '1px solid var(--border)',
        borderLeft: `3px solid ${platformColor}`,
        borderRadius: 'var(--radius)',
        padding: '12px 14px',
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
      }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <span
          style={{
            background: platformColor + '22',
            color: platformColor,
            borderRadius: 999,
            padding: '2px 8px',
            fontSize: 11,
            fontWeight: 600,
            textTransform: 'capitalize',
          }}
        >
          {source_platform}
        </span>
        {author_handle && (
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{author_handle}</span>
        )}
        {product_model && (
          <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>{product_model}</span>
        )}
        <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginLeft: 'auto' }}>{date}</span>
      </div>

      {/* Quote text */}
      <p
        style={{
          margin: 0,
          fontSize: 13,
          color: 'var(--text-primary)',
          lineHeight: 1.6,
          fontStyle: 'italic',
        }}
      >
        "{text}"
      </p>

      {/* Footer: sentiment + sarcasm flag + rating + link */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <SentimentBadge label={derived.overall_sentiment} score={derived.compound_score} size="sm" />
        {derived.sarcasm_flag && (
          <span
            style={{
              background: 'var(--mixed)22',
              color: 'var(--mixed)',
              borderRadius: 999,
              padding: '2px 8px',
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            Sarcasm detected
          </span>
        )}
        {rating !== undefined && (
          <span style={{ fontSize: 12, color: 'var(--neutral)' }}>{'★'.repeat(Math.round(rating))} {rating}/5</span>
        )}
        {source_url && (
          <a
            href={source_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: 11, marginLeft: 'auto', color: 'var(--accent)' }}
          >
            View source ↗
          </a>
        )}
      </div>

      {/* Aspect chips */}
      {derived.aspects.length > 0 && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {derived.aspects.map((a) => (
            <span
              key={a.name}
              style={{
                fontSize: 11,
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                borderRadius: 4,
                padding: '2px 6px',
                color: 'var(--text-secondary)',
              }}
            >
              {a.name}: <span style={{ color: a.polarity === 'positive' ? 'var(--positive)' : a.polarity === 'negative' ? 'var(--negative)' : 'var(--neutral)' }}>{a.snippet}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
