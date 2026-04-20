import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: '◉' },
  { to: '/products', label: 'Products', icon: '◈' },
  { to: '/platforms', label: 'Platforms', icon: '◆' },
  { to: '/topics', label: 'Topics', icon: '◇' },
  { to: '/alerts', label: 'Alerts', icon: '⚠' },
];

export function Sidebar() {
  return (
    <nav
      style={{
        width: 56,
        minHeight: '100vh',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: 16,
        gap: 4,
        flexShrink: 0,
      }}
    >
      {/* Logo mark */}
      <div
        style={{
          width: 32,
          height: 32,
          background: 'var(--accent)',
          borderRadius: 8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontWeight: 700,
          fontSize: 14,
          marginBottom: 16,
        }}
      >
        SN
      </div>

      {NAV_ITEMS.map(({ to, label, icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          title={label}
          style={({ isActive }) => ({
            width: 40,
            height: 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 8,
            background: isActive ? 'var(--accent)' : 'transparent',
            color: isActive ? '#fff' : 'var(--text-secondary)',
            fontSize: 18,
            textDecoration: 'none',
            transition: 'background 0.15s, color 0.15s',
          })}
        >
          {icon}
        </NavLink>
      ))}
    </nav>
  );
}
