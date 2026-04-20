import { useFilterStore } from '../../store/filterStore';
import type { Brand, Category, SourcePlatform } from '../../types';

const BRAND_OPTIONS: { value: Brand; label: string }[] = [
  { value: 'shark', label: 'Shark' },
  { value: 'ninja', label: 'Ninja' },
  { value: 'dyson', label: 'Dyson' },
  { value: 'irobot', label: 'iRobot' },
  { value: 'roborock', label: 'Roborock' },
  { value: 'kitchenaid', label: 'KitchenAid' },
  { value: 'breville', label: 'Breville' },
  { value: 'keurig', label: 'Keurig' },
  { value: 'delonghi', label: "De'Longhi" },
];

const CATEGORY_OPTIONS: { value: Category; label: string }[] = [
  { value: 'robot_vacuum', label: 'Robot Vacuum' },
  { value: 'cordless_stick', label: 'Cordless Stick' },
  { value: 'upright', label: 'Upright' },
  { value: 'air_fryer', label: 'Air Fryer' },
  { value: 'pressure_cooker', label: 'Pressure Cooker' },
  { value: 'blender', label: 'Blender' },
  { value: 'ice_cream_maker', label: 'Ice Cream Maker' },
  { value: 'coffee', label: 'Coffee' },
  { value: 'air_purifier', label: 'Air Purifier' },
];

const PLATFORM_OPTIONS: { value: SourcePlatform; label: string }[] = [
  { value: 'reddit', label: 'Reddit' },
  { value: 'amazon', label: 'Amazon' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'trustpilot', label: 'Trustpilot' },
  { value: 'twitter', label: 'Twitter/X' },
];

const DATE_OPTIONS: { value: '7d' | '30d' | '90d'; label: string }[] = [
  { value: '7d', label: '7 days' },
  { value: '30d', label: '30 days' },
  { value: '90d', label: '90 days' },
];

const selectStyle: React.CSSProperties = {
  background: 'var(--bg-surface-raised)',
  color: 'var(--text-primary)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: '4px 8px',
  fontSize: 13,
  outline: 'none',
  cursor: 'pointer',
};

export function FilterBar() {
  const { brands, categories, platforms, dateRange, setBrands, setCategories, setPlatforms, setDateRange, reset } =
    useFilterStore();

  function handleMultiSelect<T extends string>(
    current: T[],
    setter: (v: T[]) => void,
    value: T
  ) {
    if (current.includes(value)) {
      setter(current.filter((v) => v !== value));
    } else {
      setter([...current, value]);
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '10px 16px',
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border)',
        flexWrap: 'wrap',
      }}
    >
      {/* Brand multi-select */}
      <FilterGroup label="Brand">
        <select
          multiple
          value={brands}
          onChange={(e) =>
            setBrands(Array.from(e.target.selectedOptions, (o) => o.value as Brand))
          }
          style={{ ...selectStyle, height: 28 }}
          size={1}
        >
          <option value="" disabled>
            All Brands
          </option>
          {BRAND_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        {brands.length > 0 && (
          <ChipList labels={brands} onRemove={(b) => handleMultiSelect(brands, setBrands, b as Brand)} />
        )}
      </FilterGroup>

      {/* Category */}
      <FilterGroup label="Category">
        <select
          multiple
          value={categories}
          onChange={(e) =>
            setCategories(Array.from(e.target.selectedOptions, (o) => o.value as Category))
          }
          style={{ ...selectStyle, height: 28 }}
          size={1}
        >
          {CATEGORY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        {categories.length > 0 && (
          <ChipList
            labels={categories}
            onRemove={(c) => handleMultiSelect(categories, setCategories, c as Category)}
          />
        )}
      </FilterGroup>

      {/* Platform */}
      <FilterGroup label="Platform">
        <select
          multiple
          value={platforms}
          onChange={(e) =>
            setPlatforms(Array.from(e.target.selectedOptions, (o) => o.value as SourcePlatform))
          }
          style={{ ...selectStyle, height: 28 }}
          size={1}
        >
          {PLATFORM_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        {platforms.length > 0 && (
          <ChipList
            labels={platforms}
            onRemove={(p) => handleMultiSelect(platforms, setPlatforms, p as SourcePlatform)}
          />
        )}
      </FilterGroup>

      {/* Date range */}
      <FilterGroup label="Date Range">
        <div style={{ display: 'flex', gap: 4 }}>
          {DATE_OPTIONS.map((o) => (
            <button
              key={o.value}
              onClick={() => setDateRange(o.value)}
              style={{
                ...selectStyle,
                background:
                  dateRange === o.value ? 'var(--accent)' : 'var(--bg-surface-raised)',
                color: dateRange === o.value ? '#fff' : 'var(--text-secondary)',
                border: '1px solid ' + (dateRange === o.value ? 'var(--accent)' : 'var(--border)'),
                padding: '4px 10px',
              }}
            >
              {o.label}
            </button>
          ))}
        </div>
      </FilterGroup>

      {/* Reset */}
      <button
        onClick={reset}
        style={{
          ...selectStyle,
          color: 'var(--text-tertiary)',
          marginLeft: 'auto',
        }}
      >
        Reset
      </button>
    </div>
  );
}

function FilterGroup({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: 1 }}>
        {label}
      </span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
        {children}
      </div>
    </div>
  );
}

function ChipList({
  labels,
  onRemove,
}: {
  labels: string[];
  onRemove: (label: string) => void;
}) {
  return (
    <>
      {labels.map((l) => (
        <span
          key={l}
          style={{
            background: 'var(--accent)',
            color: '#fff',
            borderRadius: 999,
            padding: '2px 8px',
            fontSize: 11,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
          }}
        >
          {l}
          <button
            onClick={() => onRemove(l)}
            style={{
              background: 'none',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              padding: 0,
              lineHeight: 1,
              fontSize: 13,
            }}
          >
            ×
          </button>
        </span>
      ))}
    </>
  );
}
