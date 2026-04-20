import type { components } from '../types/api';

type TopicExplorerResponse = components['schemas']['TopicExplorerResponse'];
type TopicCluster = components['schemas']['TopicCluster'];
type ComparativeTopicResponse = components['schemas']['ComparativeTopicResponse'];

function makeTrend(baseScore: number, momentum: number): components['schemas']['TimeseriesPoint'][] {
  return Array.from({ length: 8 }, (_, i) => ({
    date: new Date(Date.now() - (7 - i) * 7 * 86400000).toISOString().split('T')[0],
    score: parseFloat(Math.max(-1, Math.min(1, baseScore + (momentum / 8) * i * 0.01)).toFixed(3)),
    mention_count: Math.floor(30 + Math.random() * 20),
  }));
}

const TOPIC_CLUSTERS: TopicCluster[] = [
  {
    topic_id: 'topic-001', label: 'Mop Streaking',
    mention_count: 342, avg_score: -0.74, momentum: -22.4, is_novel: false,
    exemplar_quotes: [
      '"The mop pad is leaving streaks on every pass — completely useless on hardwood."',
      '"Tried everything but the mopping function just smears dirt around."',
    ],
    trend: makeTrend(-0.74, -22.4),
  },
  {
    topic_id: 'topic-002', label: 'Battery Life',
    mention_count: 298, avg_score: -0.42, momentum: -9.1, is_novel: false,
    exemplar_quotes: [
      '"Battery barely lasts 40 minutes on a full charge after 6 months."',
      '"Oh great, dies halfway through the living room. Loving the runtime."',
    ],
    trend: makeTrend(-0.42, -9.1),
  },
  {
    topic_id: 'topic-003', label: 'Navigation & Mapping',
    mention_count: 421, avg_score: 0.76, momentum: 8.7, is_novel: false,
    exemplar_quotes: [
      '"The lidar mapping is genuinely impressive — mapped my whole place in one run."',
      '"No-go zones work perfectly and the app map is super accurate."',
    ],
    trend: makeTrend(0.76, 8.7),
  },
  {
    topic_id: 'topic-004', label: 'App Connectivity',
    mention_count: 275, avg_score: -0.38, momentum: -6.8, is_novel: false,
    exemplar_quotes: [
      '"App crashes every time I try to set a schedule. Three firmware updates and still broken."',
      '"The connectivity drops constantly — have to re-pair it weekly."',
    ],
    trend: makeTrend(-0.38, -6.8),
  },
  {
    topic_id: 'topic-005', label: 'Suction Power',
    mention_count: 489, avg_score: 0.83, momentum: 12.1, is_novel: false,
    exemplar_quotes: [
      '"Suction is incredible — picks up pet hair I did not even know was there."',
      '"The cyclonic suction on this thing is no joke. Best vacuum I have owned."',
    ],
    trend: makeTrend(0.83, 12.1),
  },
  {
    topic_id: 'topic-006', label: 'UV Detection',
    mention_count: 289, avg_score: 0.88, momentum: 22.3, is_novel: false,
    exemplar_quotes: [
      '"The UV reveal feature actually showed how dirty my mattress was — mind-blowing."',
      '"Worth every penny just for the UV light. You cannot unsee what it reveals."',
    ],
    trend: makeTrend(0.88, 22.3),
  },
  {
    topic_id: 'topic-007', label: 'Self-Empty Base',
    mention_count: 234, avg_score: 0.48, momentum: 3.2, is_novel: false,
    exemplar_quotes: [
      '"The self-empty base is loud but I only have to empty it once a month."',
      '"Love not having to deal with the dustbin constantly.",',
    ],
    trend: makeTrend(0.48, 3.2),
  },
  {
    topic_id: 'topic-008', label: 'HEPA & Brushroll Maintenance',
    mention_count: 198, avg_score: -0.58, momentum: -4.5, is_novel: false,
    exemplar_quotes: [
      '"HEPA filter needs replacing way too often — expensive to maintain."',
      '"The brushroll tangles on long hair every single run."',
    ],
    trend: makeTrend(-0.58, -4.5),
  },
  {
    topic_id: 'topic-009', label: 'Value for Money',
    mention_count: 312, avg_score: 0.12, momentum: -2.1, is_novel: false,
    exemplar_quotes: [
      '"Expensive but the performance justifies it — barely."',
      '"For $600 I expected it not to need a replacement part after 3 months."',
    ],
    trend: makeTrend(0.12, -2.1),
  },
  {
    topic_id: 'topic-010', label: 'Edge Cleaning',
    mention_count: 187, avg_score: 0.55, momentum: 5.4, is_novel: false,
    exemplar_quotes: [
      '"Shark is way better than my old Dyson at edge cleaning — actually gets into corners."',
      '"Edge detection is excellent, no more manual touch-ups along baseboards."',
    ],
    trend: makeTrend(0.55, 5.4),
  },
  {
    topic_id: 'topic-011', label: 'Charging Dock LED Flickering',
    mention_count: 12, avg_score: -0.61, momentum: 0.42, is_novel: true,
    exemplar_quotes: [
      '"The LED on the charging dock flickers constantly — started happening 2 weeks ago."',
      '"Anyone else noticing the dock light flashing every few seconds? Support says it is normal but it looks wrong."',
    ],
    trend: makeTrend(-0.61, 0.42),
  },
];

export const FIXTURE_TOPIC_EXPLORER: TopicExplorerResponse = {
  topics: TOPIC_CLUSTERS,
};

export const FIXTURE_TOPIC_COMPARATIVE: ComparativeTopicResponse = {
  brand_a: 'shark',
  brand_b: 'dyson',
  share_of_aspect: [
    { brand: 'shark', aspect: 'suction', mention_share: 0.557, avg_score: 0.83 },
    { brand: 'dyson', aspect: 'suction', mention_share: 0.443, avg_score: 0.88 },
    { brand: 'shark', aspect: 'navigation', mention_share: 0.744, avg_score: 0.76 },
    { brand: 'dyson', aspect: 'navigation', mention_share: 0.256, avg_score: 0.52 },
    { brand: 'shark', aspect: 'edge_cleaning', mention_share: 0.482, avg_score: 0.55 },
    { brand: 'dyson', aspect: 'edge_cleaning', mention_share: 0.518, avg_score: 0.42 },
    { brand: 'shark', aspect: 'battery', mention_share: 0.549, avg_score: -0.42 },
    { brand: 'dyson', aspect: 'battery', mention_share: 0.451, avg_score: 0.55 },
    { brand: 'shark', aspect: 'value', mention_share: 0.493, avg_score: 0.12 },
    { brand: 'dyson', aspect: 'value', mention_share: 0.507, avg_score: -0.65 },
  ],
};
