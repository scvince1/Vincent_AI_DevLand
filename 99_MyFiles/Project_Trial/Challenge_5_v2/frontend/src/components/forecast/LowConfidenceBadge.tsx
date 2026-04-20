interface Props {
  mentionCount: number;
  windowDays: number;
}

/**
 * Amber badge shown in the ForecastPanel card header when the backend
 * returns low_confidence: true (fewer than 50 mentions or < 14-day window).
 * Renders in the card header, NOT overlaid on the chart canvas.
 */
export function LowConfidenceBadge({ mentionCount, windowDays }: Props) {
  return (
    <span
      aria-label={`Low confidence forecast — ${mentionCount} mentions over ${windowDays} days`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        fontSize: 11,
        fontWeight: 600,
        color: 'var(--color-caution)',
        background: 'rgba(245, 166, 35, 0.12)',
        border: '1px solid rgba(245, 166, 35, 0.35)',
        borderRadius: 999,
        padding: '2px 8px',
      }}
    >
      <span
        aria-hidden="true"
        style={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: 'var(--color-caution)',
          display: 'inline-block',
          flexShrink: 0,
        }}
      />
      Low confidence &mdash; {mentionCount} mentions over {windowDays} days
    </span>
  );
}
