import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { FilterBar } from '../filters/FilterBar';
import { EvidenceDrilldown } from '../shared/EvidenceDrilldown';
import { FilterUrlSync } from './FilterUrlSync';

export function AppLayout() {
  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* URL sync — reads URL on mount, writes URL on filter change */}
      <FilterUrlSync />

      <Sidebar />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Filter bar scrolls horizontally on mobile (M5 responsive) */}
        <div className="filter-bar-scroll">
          <FilterBar />
        </div>

        <main
          style={{
            flex: 1,
            overflow: 'auto',
            padding: '24px 28px',
            background: 'var(--bg-base)',
          }}
          role="main"
        >
          <Outlet />
        </main>
      </div>

      {/* Global evidence drilldown panel (REQ-006) */}
      <EvidenceDrilldown />
    </div>
  );
}
