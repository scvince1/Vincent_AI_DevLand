import { create } from 'zustand';
import type { Brand, Category, SourcePlatform } from '../types';

export interface FilterState {
  brands: Brand[];
  categories: Category[];
  platforms: SourcePlatform[];
  dateRange: '7d' | '30d' | '90d' | 'custom';
  dateFrom?: string; // ISO-8601, only when dateRange === 'custom'
  dateTo?: string;
  productModel?: string; // set on Product Analysis page
}

interface FilterActions {
  setBrands: (brands: Brand[]) => void;
  setCategories: (categories: Category[]) => void;
  setPlatforms: (platforms: SourcePlatform[]) => void;
  setDateRange: (range: FilterState['dateRange'], from?: string, to?: string) => void;
  setProductModel: (model: string | undefined) => void;
  reset: () => void;
  toApiParams: () => Record<string, string | string[] | undefined>;
}

const DEFAULT: FilterState = {
  brands: [],
  categories: [],
  platforms: [],
  dateRange: '30d',
};

function dateRangeToFromTo(range: FilterState['dateRange']): { dateFrom?: string; dateTo?: string } {
  if (range === 'custom') return {};
  const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - days);
  return {
    dateFrom: from.toISOString().split('T')[0],
    dateTo: to.toISOString().split('T')[0],
  };
}

export const useFilterStore = create<FilterState & FilterActions>((set, get) => ({
  ...DEFAULT,

  setBrands: (brands) => set({ brands }),
  setCategories: (categories) => set({ categories }),
  setPlatforms: (platforms) => set({ platforms }),
  setDateRange: (dateRange, dateFrom, dateTo) => {
    if (dateRange === 'custom') {
      set({ dateRange, dateFrom, dateTo });
    } else {
      const { dateFrom: f, dateTo: t } = dateRangeToFromTo(dateRange);
      set({ dateRange, dateFrom: f, dateTo: t });
    }
  },
  setProductModel: (productModel) => set({ productModel }),
  reset: () => set(DEFAULT),

  toApiParams: () => {
    const s = get();
    const { dateFrom, dateTo } = s.dateRange !== 'custom'
      ? dateRangeToFromTo(s.dateRange)
      : { dateFrom: s.dateFrom, dateTo: s.dateTo };
    return {
      brands: s.brands.length ? s.brands : undefined,
      categories: s.categories.length ? s.categories : undefined,
      platforms: s.platforms.length ? s.platforms : undefined,
      date_from: dateFrom,
      date_to: dateTo,
      product_model: s.productModel,
    };
  },
}));
