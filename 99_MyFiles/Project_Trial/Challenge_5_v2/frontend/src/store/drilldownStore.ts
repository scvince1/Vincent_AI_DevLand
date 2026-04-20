import { create } from 'zustand';
import type { FilterState } from './filterStore';

export interface DrilldownContext {
  title: string;
  total_mentions: number;
  sentiment_score: number;
  filters: Partial<FilterState>;
  mention_ids?: string[]; // if already known (e.g. from alert page)
  aspect?: string; // to filter by aspect in the API call
}

interface DrilldownStore {
  open: boolean;
  context: DrilldownContext | null;
  openDrilldown: (ctx: DrilldownContext) => void;
  closeDrilldown: () => void;
}

export const useDrilldownStore = create<DrilldownStore>((set) => ({
  open: false,
  context: null,
  openDrilldown: (context) => set({ open: true, context }),
  closeDrilldown: () => set({ open: false, context: null }),
}));
