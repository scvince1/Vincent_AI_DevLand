import { useEffect, useState } from 'react';
import { useDrilldownStore } from '../../store/drilldownStore';
import { fetchDrilldownMentions } from '../../api/endpoints';
import type { Mention } from '../../types';
import { MentionQuote } from './MentionQuote';
import { SentimentBadge } from './SentimentBadge';
import { COLORS } from '../../theme';

export function EvidenceDrilldown() {
  const { open, context, closeDrilldown } = useDrilldownStore();
  const [mentions, setMentions] = useState<Mention[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open || !context) return;
    setLoading(true);
    setMentions([]);

    const load = async () => {
      const f = context.filters as Partial<import('../../store/filterStore').FilterState>;
      const results = await fetchDrilldownMentions({
        brand: f.brands?.[0],
        platform: f.platforms?.[0],
        product_model: f.productModel,
        topic_id: context.aspect,
        limit: 10,
      });
      setMentions(results);
      setLoading(false);
    };

    load().catch(() => setLoading(false));
  }, [open, context]);

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeDrilldown();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [closeDrilldown]);

  if (!open || !context) return null;

  const score = context.sentiment_score;
  const scoreLabel = score > 0.2 ? 'positive' : score < -0.2 ? 'negative' : 'neutral';
  const positivePct = Math.round((mentions.filter((m) => m.derived.overall_sentiment === 'positive').length / Math.max(1, mentions.length)) * 100);
  const negativePct = Math.round((mentions.filter((m) => m.derived.overall_sentiment === 'negative').length / Math.max(1, mentions.length)) * 100);
  const sarcasmCount = mentions.filter((m) => m.derived.sarcasm_flag).length;

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={closeDrilldown}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.45)',
          zIndex: 100,
        }}
      />

      {/* Side panel — slides in from right */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label={context.title}
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: 480,
          maxWidth: '100vw',
          background: 'var(--bg-surface)',
          borderLeft: '1px solid var(--border)',
          zIndex: 101,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          animation: 'slideInFromRight 220ms ease-out',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 12,
          }}
        >
          <div style={{ flex: 1 }}>
            <h3 style={{ margin: 0, fontSize: 15, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {context.title}
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
              Backed by{' '}
              <strong style={{ color: 'var(--text-primary)' }}>
                {context.total_mentions.toLocaleString()} mentions
              </strong>
            </p>
          </div>
          <button
            onClick={closeDrilldown}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: 20,
              lineHeight: 1,
              cursor: 'pointer',
              padding: 4,
            }}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Sentiment summary bar */}
        <div
          style={{
            padding: '12px 20px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <SentimentBadge label={scoreLabel} score={context.sentiment_score} />
          <div style={{ flex: 1, height: 8, background: 'var(--bg-base)', borderRadius: 4, display: 'flex', overflow: 'hidden' }}>
            <div style={{ width: `${positivePct}%`, background: COLORS.positive }} />
            <div style={{ width: `${negativePct}%`, background: COLORS.negative }} />
            <div style={{ flex: 1, background: COLORS.neutral + '44' }} />
          </div>
          <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
            {positivePct}% pos / {negativePct}% neg
          </span>
        </div>

        {sarcasmCount > 0 && (
          <div
            style={{
              margin: '0 20px',
              padding: '8px 12px',
              background: 'var(--mixed)22',
              borderRadius: 'var(--radius-sm)',
              fontSize: 12,
              color: 'var(--mixed)',
              marginTop: 12,
            }}
          >
            {sarcasmCount} mention{sarcasmCount > 1 ? 's' : ''} flagged as sarcasm by the NLP pipeline
          </div>
        )}

        {/* Mentions list */}
        <div
          style={{
            flex: 1,
            overflow: 'auto',
            padding: '12px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}
        >
          {loading && (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: 40 }}>
              Loading mentions...
            </p>
          )}
          {!loading && mentions.length === 0 && (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: 40 }}>
              No mentions found for this filter combination.
            </p>
          )}
          {mentions.map((m) => (
            <MentionQuote key={m.mention_id} mention={m} />
          ))}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '12px 20px',
            borderTop: '1px solid var(--border)',
            fontSize: 12,
            color: 'var(--text-tertiary)',
            textAlign: 'center',
          }}
        >
          Showing {mentions.length} representative mentions of {context.total_mentions.toLocaleString()} total
        </div>
      </div>
    </>
  );
}
