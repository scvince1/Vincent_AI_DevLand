import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFilterStore } from '../../store/filterStore';
import type { Brand, Category, SourcePlatform } from '../../types';

/**
 * Syncs the Zustand filter store with the URL search params in both directions.
 * Mount this once inside <BrowserRouter> (e.g. in AppLayout).
 *
 * On mount: reads URL params → hydrates store.
 * On store change: serializes store → updates URL (replaceState, no nav history entry).
 */
export function FilterUrlSync() {
  const [searchParams, setSearchParams] = useSearchParams();

  const {
    brands,
    categories,
    platforms,
    dateRange,
    dateFrom,
    dateTo,
    productModel,
    setBrands,
    setCategories,
    setPlatforms,
    setDateRange,
    setProductModel,
  } = useFilterStore();

  // On mount: hydrate store from current URL params (once only)
  useEffect(() => {
    const brandsParam = searchParams.getAll('brands') as Brand[];
    const categoriesParam = searchParams.getAll('categories') as Category[];
    const platformsParam = searchParams.getAll('platforms') as SourcePlatform[];
    const dateRangeParam = searchParams.get('dateRange') as '7d' | '30d' | '90d' | 'custom' | null;
    const dateFromParam = searchParams.get('dateFrom') ?? undefined;
    const dateToParam = searchParams.get('dateTo') ?? undefined;
    const productModelParam = searchParams.get('productModel') ?? undefined;

    if (brandsParam.length) setBrands(brandsParam);
    if (categoriesParam.length) setCategories(categoriesParam);
    if (platformsParam.length) setPlatforms(platformsParam);
    if (dateRangeParam) setDateRange(dateRangeParam, dateFromParam, dateToParam);
    if (productModelParam) setProductModel(productModelParam);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // On store change: push new state to URL
  useEffect(() => {
    const params = new URLSearchParams();
    brands.forEach((b) => params.append('brands', b));
    categories.forEach((c) => params.append('categories', c));
    platforms.forEach((p) => params.append('platforms', p));
    params.set('dateRange', dateRange);
    if (dateRange === 'custom') {
      if (dateFrom) params.set('dateFrom', dateFrom);
      if (dateTo) params.set('dateTo', dateTo);
    }
    if (productModel) params.set('productModel', productModel);

    setSearchParams(params, { replace: true });
  }, [brands, categories, platforms, dateRange, dateFrom, dateTo, productModel, setSearchParams]);

  return null;
}
