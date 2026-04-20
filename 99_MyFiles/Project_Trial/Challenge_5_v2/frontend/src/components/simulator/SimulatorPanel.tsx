import { useState } from 'react';
import type { SimulationResult } from '../../api/endpoints';
import { postSimulate } from '../../api/endpoints';
import { SimulatedSegmentCard } from './SimulatedSegmentCard';

// ─── Disclaimer banner ─────────────────────────────────────────────────────────

function DisclaimerBanner({ text }: { text: string }) {
  return (
    <div
      role="note"
      aria-label="Simulation disclaimer"
      style={{
        borderLeft: '4px solid var(--color-caution)',
        background: 'rgba(245, 166, 35, 0.06)',
        borderRadius: 'var(--radius-sm)',
        padding: '10px 14px',
        marginBottom: 16,
      }}
    >
      <p style={{ margin: 0, fontSize: 12, fontStyle: 'italic', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
        {text}
      </p>
    </div>
  );
}

// ─── Main component ─────────────────────────────────────────────────────────────

interface SimulatorPanelProps {
  productModel: string | null;
  /** Mention count from current product context — used in loading copy */
  inputMentionCount?: number;
}

export function SimulatorPanel({ productModel, inputMentionCount }: SimulatorPanelProps) {
  const [scenario, setScenario] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scenario.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await postSimulate({
        scenario: scenario.trim(),
        product_model: productModel ?? undefined,
      });
      setResult(res);
    } catch (err) {
      const isTimeout =
        err instanceof Error &&
        (err.name === 'TimeoutError' || err.message.includes('timeout') || err.message.includes('abort'));
      setError(
        isTimeout
          ? 'Simulation timed out — the model took too long to respond.'
          : 'Simulation failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const loadingMentionCopy = inputMentionCount
    ? `Running simulation on ${inputMentionCount.toLocaleString()} real consumer mentions...`
    : 'Running simulation on real consumer mentions...';

  return (
    <div className="section-card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Card header */}
      <h3 className="section-label" style={{ margin: 0 }}>
        What-If Simulator
      </h3>

      {/* Input form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <label htmlFor="simulator-input" style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
          What if...
        </label>
        <textarea
          id="simulator-input"
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          placeholder="What if Shark launched a $99 budget version targeting renters?"
          rows={3}
          disabled={loading}
          aria-label="Simulation scenario input"
          style={{
            width: '100%',
            background: 'var(--bg-surface-raised)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '10px 12px',
            fontSize: 13,
            fontFamily: 'inherit',
            lineHeight: 1.5,
            resize: 'vertical',
            boxSizing: 'border-box',
          }}
        />
        <p style={{ margin: 0, fontSize: 11, color: 'var(--text-tertiary)' }}>
          Be specific — simulations are grounded in real consumer mentions for the selected product.
        </p>
        <div>
          <button
            type="submit"
            disabled={loading || !scenario.trim()}
            className="btn btn-primary"
            aria-label="Submit simulation scenario"
          >
            {loading ? 'Simulating...' : 'Simulate reaction'}
          </button>
        </div>
      </form>

      {/* Loading state */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }} aria-live="polite" aria-label={loadingMentionCopy}>
          <p className="section-label" style={{ margin: 0, color: 'var(--text-tertiary)' }}>
            {loadingMentionCopy}
          </p>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: 80, borderRadius: 'var(--radius)' }} />
          ))}
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className="error-state">
          <p className="error-state-msg">{error}</p>
          <button
            className="btn btn-ghost"
            onClick={() => setError(null)}
            aria-label="Dismiss error and try again"
          >
            Try again
          </button>
        </div>
      )}

      {/* Results */}
      {!loading && result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {/* Disclaimer banner — always visible, verbatim, amber accent */}
          <DisclaimerBanner text={result.overall_disclaimer} />

          {/* Segment cards */}
          {result.segments.length === 0 ? (
            <div className="empty-state">
              <span className="empty-state-icon" aria-hidden="true">○</span>
              <p className="empty-state-title">No segments returned</p>
              <p className="empty-state-desc">Try a more specific scenario.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {result.segments.map((seg, i) => (
                <SimulatedSegmentCard key={i} segment={seg} />
              ))}
            </div>
          )}

          {/* Model metadata footer */}
          <p
            style={{
              margin: '12px 0 0',
              fontSize: 11,
              color: 'var(--text-tertiary)',
            }}
          >
            Model: {result.model_used}
            {result.tokens_consumed > 0 && ` · ${result.tokens_consumed.toLocaleString()} tokens`}
          </p>
        </div>
      )}
    </div>
  );
}
