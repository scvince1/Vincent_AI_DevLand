import type { components } from '../types/api';

type ProductSummary = components['schemas']['ProductSummary'];
type ProductAspectResponse = components['schemas']['ProductAspectResponse'];
type AspectTrend = components['schemas']['AspectTrend'];

function makeAspect(
  name: string,
  avgScore: number,
  count: number,
  severity: number,
  trendDelta = 0.0
): AspectTrend {
  const sparkline = Array.from({ length: 8 }, (_, i) => {
    const noise = (Math.random() - 0.5) * 0.1;
    return parseFloat(Math.max(-1, Math.min(1, avgScore + noise + (trendDelta / 8) * i)).toFixed(3));
  });
  return { aspect: name, mention_count: count, avg_score: avgScore, trend_delta: trendDelta, severity, sparkline };
}

// Slim list — matches /api/products (no aspects)
export const FIXTURE_PRODUCTS: ProductSummary[] = [
  { brand: 'shark', category: 'robot_vacuum', product_model: 'PowerDetect UV Reveal', overall_score: 0.18, mention_count: 2341 },
  { brand: 'shark', category: 'robot_vacuum', product_model: 'Shark Matrix', overall_score: 0.35, mention_count: 1823 },
  { brand: 'shark', category: 'cordless_stick', product_model: 'Shark Stratos', overall_score: 0.42, mention_count: 1456 },
  { brand: 'ninja', category: 'air_fryer', product_model: 'Ninja Foodi DualZone', overall_score: 0.58, mention_count: 1289 },
  { brand: 'ninja', category: 'ice_cream_maker', product_model: 'Ninja Creami Scoop & Swirl', overall_score: 0.62, mention_count: 987 },
  { brand: 'dyson', category: 'cordless_stick', product_model: 'Dyson V15 Detect', overall_score: 0.45, mention_count: 1102 },
  { brand: 'irobot', category: 'robot_vacuum', product_model: 'iRobot Roomba j9+', overall_score: 0.38, mention_count: 891 },
  { brand: 'ninja', category: 'coffee', product_model: 'Ninja Espresso Bar', overall_score: 0.31, mention_count: 743 },
];

// Full aspect responses — matches /api/products/{model}/aspects
export const FIXTURE_PRODUCT_ASPECTS: ProductAspectResponse[] = [
  {
    product_model: 'PowerDetect UV Reveal', brand: 'shark', category: 'robot_vacuum',
    aspects: [
      makeAspect('suction', 0.82, 421, 5, 2.1),
      makeAspect('navigation', 0.76, 310, 5, 1.5),
      makeAspect('uv_detection', 0.88, 289, 3, 3.2),
      makeAspect('mop_pad', -0.71, 342, 92, -18.4),
      makeAspect('battery', -0.45, 198, 68, -9.2),
      makeAspect('app', -0.38, 175, 54, -6.8),
      makeAspect('noise', -0.22, 143, 32, -1.5),
      makeAspect('self_empty_base', 0.55, 201, 10, 0.8),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'Shark Matrix', brand: 'shark', category: 'robot_vacuum',
    aspects: [
      makeAspect('suction', 0.79, 380, 5, 1.8),
      makeAspect('navigation', 0.65, 275, 8, 0.9),
      makeAspect('self_empty_base', 0.48, 195, 12, 0.5),
      makeAspect('battery', 0.32, 160, 18, -0.3),
      makeAspect('app', -0.18, 142, 38, -2.1),
      makeAspect('noise', -0.35, 131, 47, -1.8),
      makeAspect('dustbin', 0.22, 118, 20, 0.2),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'Shark Stratos', brand: 'shark', category: 'cordless_stick',
    aspects: [
      makeAspect('suction', 0.85, 392, 4, 1.2),
      makeAspect('runtime', 0.38, 267, 20, -0.5),
      makeAspect('hepa_filter', -0.28, 189, 43, -3.1),
      makeAspect('brushroll', -0.31, 201, 48, -2.8),
      makeAspect('dustbin', -0.15, 176, 32, -1.0),
      makeAspect('weight', 0.52, 143, 8, 0.4),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'Ninja Foodi DualZone', brand: 'ninja', category: 'air_fryer',
    aspects: [
      makeAspect('cooking_performance', 0.82, 412, 4, 1.5),
      makeAspect('capacity', 0.65, 310, 7, 0.3),
      makeAspect('basket_coating', -0.42, 198, 61, -11.8),
      makeAspect('noise', -0.12, 145, 25, -0.8),
      makeAspect('ease_of_use', 0.72, 267, 5, 0.6),
      makeAspect('cleaning', 0.38, 201, 18, 0.2),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'Ninja Creami Scoop & Swirl', brand: 'ninja', category: 'ice_cream_maker',
    aspects: [
      makeAspect('texture_quality', 0.88, 341, 3, 1.1),
      makeAspect('ease_of_use', 0.75, 298, 5, 0.5),
      makeAspect('maintenance', -0.22, 178, 35, -2.0),
      makeAspect('noise', -0.48, 201, 66, -15.2),
      makeAspect('container', 0.42, 156, 12, 0.3),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'Dyson V15 Detect', brand: 'dyson', category: 'cordless_stick',
    aspects: [
      makeAspect('suction', 0.88, 389, 4, 1.0),
      makeAspect('battery', 0.55, 245, 10, 0.3),
      makeAspect('attachments', 0.62, 212, 8, 0.4),
      makeAspect('price', -0.65, 321, 78, -2.5),
      makeAspect('dustbin', -0.12, 156, 28, -0.5),
      makeAspect('noise', 0.18, 134, 22, 0.1),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'iRobot Roomba j9+', brand: 'irobot', category: 'robot_vacuum',
    aspects: [
      makeAspect('navigation', 0.82, 312, 5, 1.2),
      makeAspect('mapping', 0.78, 289, 5, 0.8),
      makeAspect('self_empty_base', 0.65, 201, 9, 0.5),
      makeAspect('suction', 0.42, 187, 16, 0.2),
      makeAspect('app', 0.55, 178, 10, 0.4),
      makeAspect('price', -0.55, 245, 72, -1.8),
    ],
    exemplar_mentions: [],
  },
  {
    product_model: 'Ninja Espresso Bar', brand: 'ninja', category: 'coffee',
    aspects: [
      makeAspect('coffee_quality', 0.68, 298, 8, 0.5),
      makeAspect('ease_of_use', 0.55, 215, 12, 0.3),
      makeAspect('descaling', -0.58, 167, 74, -5.5),
      makeAspect('pod_compartment', -0.45, 142, 63, -14.1),
      makeAspect('brew_speed', -0.32, 125, 46, -2.1),
      makeAspect('price', 0.72, 201, 7, 0.6),
    ],
    exemplar_mentions: [],
  },
];

export function getProductByModel(model: string): ProductAspectResponse | undefined {
  return FIXTURE_PRODUCT_ASPECTS.find((p) => p.product_model === model);
}
