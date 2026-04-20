interface Props {
  score: number; // 0-100
  showLabel?: boolean;
}

export function SeverityBar({ score, showLabel = true }: Props) {
  const color =
    score >= 75 ? 'var(--severity-high)' : score >= 50 ? 'var(--severity-medium)' : 'var(--severity-low)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div
        style={{
          flex: 1,
          height: 6,
          background: 'var(--border)',
          borderRadius: 3,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${score}%`,
            height: '100%',
            background: color,
            borderRadius: 3,
            transition: 'width 0.4s ease',
          }}
        />
      </div>
      {showLabel && (
        <span style={{ fontSize: 12, color, fontWeight: 600, minWidth: 28 }}>{score}</span>
      )}
    </div>
  );
}
