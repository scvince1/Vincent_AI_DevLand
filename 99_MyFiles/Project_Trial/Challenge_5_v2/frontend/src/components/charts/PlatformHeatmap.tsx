import React from 'react';
import type { PlatformComparisonResponse, SourcePlatform } from '../../types';
import { COLORS } from '../../theme';

const ALL_ASPECTS = [
  'suction', 'navigation', 'battery', 'app', 'mop_pad',
  'noise', 'value', 'firmware', 'warranty', 'ease_of_use',
  'customer_service', 'durability', 'uv_detection', 'design',
];

interface Props {
  data: PlatformComparisonResponse;
  onCellClick?: (platform: SourcePlatform, aspect: string, score: number, count: number) => void;
}

function scoreToHeatColor(score: number): string {
  const s = Math.max(-1, Math.min(1, score));
  if (s >= 0) {
    const t = s;
    const r = Math.round(0xf0 + t * (0x3e - 0xf0));
    const g = Math.round(0xb4 + t * (0xcf - 0xb4));
    const b = Math.round(0x29 + t * (0x8e - 0x29));
    return `rgb(${r},${g},${b})`;
  } else {
    const t = -s;
    const r = Math.round(0xf0 + t * (0xf0 - 0xf0));
    const g = Math.round(0xb4 + t * (0x52 - 0xb4));
    const b = Math.round(0x29 + t * (0x52 - 0x29));
    return `rgb(${r},${g},${b})`;
  }
}

export function PlatformHeatmap({ data, onCellClick }: Props) {
  // Build map: platform -> aspect -> {score, count}
  const map: Record<string, Record<string, { score: number; count: number }>> = {};
  const usedAspects = new Set<string>();

  for (const cell of data.grid) {
    if (!map[cell.platform]) map[cell.platform] = {};
    map[cell.platform][cell.aspect] = {
      score: cell.sentiment_score,
      count: cell.mention_count,
    };
    usedAspects.add(cell.aspect);
  }

  const platforms = [...new Set(data.grid.map((c) => c.platform))] as SourcePlatform[];
  const aspects = ALL_ASPECTS.filter((a) => usedAspects.has(a));
  const gridTemplateColumns = `180px repeat(${aspects.length}, 1fr)`;

  const headerStyle: React.CSSProperties = {
    padding: '8px 10px',
    fontSize: 11,
    fontWeight: 600,
    color: COLORS.textTertiary,
    borderBottom: `1px solid ${COLORS.border}`,
    textAlign: 'center' as const,
    background: 'var(--bg-surface)',
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns, minWidth: 600 }}>
        {/* Header row */}
        <div style={{ ...headerStyle, textAlign: 'left' }}>Platform</div>
        {aspects.map((a) => (
          <div key={a} style={headerStyle}>
            {a.replace(/_/g, ' ')}
          </div>
        ))}

        {/* Data rows */}
        {platforms.map((platform) => (
          <React.Fragment key={platform}>
            <div
              style={{
                padding: '10px 12px',
                fontWeight: 600,
                fontSize: 13,
                color: 'var(--text-primary)',
                textTransform: 'capitalize',
                borderBottom: `1px solid ${COLORS.border}`,
                background: 'var(--bg-surface)',
              }}
            >
              {platform}
            </div>

            {aspects.map((a) => {
              const cell = map[platform]?.[a];
              const bgColor = cell ? scoreToHeatColor(cell.score) : 'transparent';
              const textColor = cell ? '#0d0f14' : COLORS.textTertiary;

              return (
                <div
                  key={a}
                  onClick={() => {
                    if (!cell || !onCellClick) return;
                    onCellClick(platform, a, cell.score, cell.count);
                  }}
                  style={{
                    padding: '10px 6px',
                    textAlign: 'center',
                    borderBottom: `1px solid ${COLORS.border}`,
                    background: bgColor,
                    cursor: cell && onCellClick ? 'pointer' : 'default',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 2,
                    transition: 'opacity 0.15s',
                  }}
                  title={cell ? `${(cell.score * 100).toFixed(0)} score, ${cell.count} mentions` : undefined}
                >
                  {cell ? (
                    <>
                      <span style={{ color: textColor, fontWeight: 700, fontSize: 13 }}>
                        {cell.score > 0 ? '+' : ''}{(cell.score * 100).toFixed(0)}
                      </span>
                      <span style={{ color: textColor, fontSize: 11, opacity: 0.75 }}>
                        {cell.count.toLocaleString()}
                      </span>
                    </>
                  ) : (
                    <span style={{ color: COLORS.textTertiary, fontSize: 12 }}>—</span>
                  )}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, fontSize: 11, color: COLORS.textTertiary }}>
        <span>Negative</span>
        <div
          style={{
            width: 120,
            height: 10,
            borderRadius: 5,
            background: `linear-gradient(to right, ${COLORS.negative}, ${COLORS.neutral}, ${COLORS.positive})`,
          }}
        />
        <span>Positive</span>
        <span style={{ marginLeft: 8 }}>· Click any cell for evidence</span>
      </div>
    </div>
  );
}
