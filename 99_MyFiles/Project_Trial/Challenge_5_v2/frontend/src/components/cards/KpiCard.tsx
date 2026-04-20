interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  delta?: number; // positive = up, negative = down
  onClick?: () => void;
}

export function KpiCard({ title, value, subtitle, delta, onClick }: Props) {
  const deltaColor = delta === undefined ? undefined : delta > 0 ? 'var(--positive)' : delta < 0 ? 'var(--negative)' : 'var(--text-tertiary)';
  const deltaSign = delta !== undefined && delta > 0 ? '+' : '';

  return (
    <div
      onClick={onClick}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={onClick ? `${title}: ${value}${subtitle ? ', ' + subtitle : ''} — click to see evidence` : undefined}
      className="section-card"
      style={{
        cursor: onClick ? 'pointer' : 'default',
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        minWidth: 160,
        flex: 1,
        transition: 'border-color 0.12s ease-out, background 0.12s ease-out',
      }}
      onMouseEnter={onClick ? (e) => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--accent)'; } : undefined}
      onMouseLeave={onClick ? (e) => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)'; } : undefined}
    >
      <span className="section-label">{title}</span>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span className="kpi-number">{value}</span>
        {delta !== undefined && (
          <span style={{ fontSize: 13, color: deltaColor, fontWeight: 600 }}>
            {deltaSign}{(delta * 100).toFixed(1)}%
          </span>
        )}
      </div>
      {subtitle && (
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{subtitle}</span>
      )}
      {onClick && (
        <span style={{ fontSize: 11, color: 'var(--accent)', marginTop: 4 }}>Click to see evidence ↗</span>
      )}
    </div>
  );
}
