import { useState } from 'react';
import type { SimulatedSegment, SimulatorPolarity as Polarity } from '../../api/endpoints';

// ─── Polarity badge ─────────────────────────────────────────────────────────────

const POLARITY_COLORS: Record<Polarity, string> = {
  positive: 'var(--positive)',
  negative: 'var(--negative)',
  neutral: 'var(--neutral)',
  mixed: 'var(--mixed)',
};

function PolarityBadge({ polarity }: { polarity: Polarity }) {
  const color = POLARITY_COLORS[polarity];
  return (
    <span
      aria-label={`Predicted reaction: ${polarity}`}
      style={{
        display: 'inline-block',
        fontSize: 11,
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.8px',
        padding: '2px 8px',
        borderRadius: 999,
        color,
        background: `${color}22`,
        border: `1px solid ${color}55`,
      }}
    >
      {polarity}
    </span>
  );
}

// ─── Main component ─────────────────────────────────────────────────────────────

interface Props {
  segment: SimulatedSegment;
}

export function SimulatedSegmentCard({ segment }: Props) {
  const [quotesOpen, setQuotesOpen] = useState(false);
  const quotes = segment.key_quotes_used ?? [];
  const quoteCount = quotes.length;

  return (
    <div
      className="section-card"
      style={{ display: 'flex', flexDirection: 'column', gap: 10 }}
    >
      {/* Header: label + polarity badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <span className="section-label" style={{ margin: 0 }}>
          {segment.segment_label}
        </span>
        <PolarityBadge polarity={segment.predicted_reaction} />
      </div>

      {/* Confidence narrative */}
      <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
        {segment.confidence_narrative}
      </p>

      {/* Quotes expander — collapsed by default */}
      {quoteCount > 0 && (
        <div>
          <button
            className="btn btn-ghost"
            aria-expanded={quotesOpen}
            aria-label={`${quotesOpen ? 'Hide' : 'Show'} ${quoteCount} supporting quote${quoteCount !== 1 ? 's' : ''}`}
            onClick={() => setQuotesOpen((v) => !v)}
            style={{ fontSize: 12 }}
          >
            {quotesOpen ? 'Hide quotes' : `Show quotes (${quoteCount})`}
          </button>

          {quotesOpen && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
              {quotes.map((quote, i) => (
                <blockquote
                  key={i}
                  style={{
                    margin: 0,
                    borderLeft: '3px solid var(--border)',
                    paddingLeft: 10,
                    fontSize: 12,
                    color: 'var(--text-secondary)',
                    fontStyle: 'italic',
                    lineHeight: 1.5,
                  }}
                >
                  "{quote.slice(0, 200)}{quote.length > 200 ? '...' : ''}"
                </blockquote>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
