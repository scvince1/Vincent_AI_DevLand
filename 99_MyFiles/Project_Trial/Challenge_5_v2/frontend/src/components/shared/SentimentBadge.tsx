import type { SentimentLabel } from '../../types';
import { sentimentColor } from '../../theme';

interface Props {
  label: SentimentLabel;
  score?: number;
  size?: 'sm' | 'md';
}

const LABEL_TEXT: Record<SentimentLabel, string> = {
  positive: 'Positive',
  negative: 'Negative',
  neutral: 'Neutral',
  mixed: 'Mixed',
};

export function SentimentBadge({ label, score, size = 'md' }: Props) {
  const color = sentimentColor(label);
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        padding: size === 'sm' ? '2px 6px' : '3px 8px',
        borderRadius: 999,
        background: color + '22',
        color,
        fontSize: size === 'sm' ? 11 : 12,
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: color, display: 'inline-block' }} />
      {LABEL_TEXT[label]}
      {score !== undefined && (
        <span style={{ opacity: 0.8, fontWeight: 400 }}>
          {score > 0 ? '+' : ''}{(score * 100).toFixed(0)}
        </span>
      )}
    </span>
  );
}
