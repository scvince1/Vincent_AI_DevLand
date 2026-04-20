---
id: subway_reference
title: Subway Nutrition Reference — Vincent's Standard Build
tags: [fitness, knowledge, nutrition, reference, sodium, restaurant]
status: confirmed
last_modified: 2026-04-15
summary: Subway 12英寸标准配置完整营养数据，Na 重点监控
---
# Subway Nutrition Reference — Vincent's Standard Build

> Source: Subway US Nutrition Information January 2026 (official PDF) + USDA FoodData Central (potassium estimates)
> Last verified: 2026-04-11
> Data origin tag (per agent rubric): `web-fetch` (Subway PDF) + `web-fetch` (USDA for K)
> Configuration: 12" Footlong / Hearty Multigrain bread / Lettuce + Spinach + Onions / Sweet Onion Teriyaki (SOT) double-sauce / Subkrunch + Oregano / **NO cheese on any item** (hard default per Vincent)
> Meal-context tags: `outside-food`, `restaurant`, `cold-cut-or-hot-press`, `Na-priority-monitoring`
> Cross-link: `targets.md` (daily Na 2300 mg UL / K 4700 mg AI), `daily-log.md` (entry format), `avocado_reference.md` (K-rebalance complement)

## Universal Adders (included in every item's totals below)

| Adder | Cal | Fat | SatFat | Chol | Na | Carb | Sug | AddSug | Prot |
|---|---|---|---|---|---|---|---|---|---|
| SOT sauce ×2 (footlong dose) | 60 | 0 | 0 | 0 | 260 | 14 | 12 | 12 | 0 |
| Subkrunch | 70 | 5 | 0 | 0 | 45 | 6 | 0 | 0 | 1 |
| Oregano | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Adder total** | **130** | **5** | **0** | **0** | **305** | **20** | **12** | **12** | **1** |

## Cheese Deduction Applied to Cheesesteaks (since Vincent orders no cheese)

2× American cheese (footlong dose, subtracted from Steak Philly / Chipotle Philly / Cheesy Garlic Steak):

| Cheese deducted | Cal | Fat | SatFat | Chol | Na | Carb | Prot |
|---|---|---|---|---|---|---|---|
| 2× American | -160 | -14 | -10 | -40 | -840 | -2 | -8 |

---

## Item 1: Sweet Onion Teriyaki Chicken

> Low sat fat but high added sugar. Watch sugar load, not sodium.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 640 | 750 | 320 | 375 |
| Total fat (g) | 19 | 21 | 9.5 | 10.5 |
| Sat fat (g) | 5 | 6 | 2.5 | 3 |
| Trans fat (g) | 0 | 0 | 0 | 0 |
| Chol (mg) | 70 | 120 | 35 | 60 |
| **Sodium (mg)** | **1,645** | **1,995** | **823** | **998** |
| Carbs (g) | 87 | 96 | 43.5 | 48 |
| Fiber (g) | 3 | 3 | 1.5 | 1.5 |
| Sugars (g) | 31 | 39 | 15.5 | 19.5 |
| **Added sugars (g)** | **27** | **34** ⚠️ | 13.5 | 17 |
| Protein (g) | 30 | 46 | 15 | 23 |
| K (mg, est.) | ~650 | ~800 | ~325 | ~400 |

## Item 2: Steak Philly (NO CHEESE)

> Cheese-strip drops Na by ~840 mg vs default. Becomes one of the lowest-Na options.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 570 | 680 | 285 | 340 |
| Total fat (g) | 21 | 26 | 10.5 | 13 |
| Sat fat (g) | ~1 | ~1 | 0.5 | 0.5 |
| Trans fat (g) | 1 | 1 | 0.5 | 0.5 |
| Chol (mg) | 45 | 100 | 23 | 50 |
| **Sodium (mg)** | **985** | **1,435** | **493** | **718** |
| Carbs (g) | 72 | 74 | 36 | 37 |
| Fiber (g) | 3 | 3 | 1.5 | 1.5 |
| Sugars (g) | 17 | 17 | 8.5 | 8.5 |
| Added sugars (g) | 15 | 15 | 7.5 | 7.5 |
| Protein (g) | 22 | 39 | 11 | 19.5 |
| K (mg, est.) | ~700 | ~850 | ~350 | ~425 |

## Item 3: Chipotle Philly (NO CHEESE)

> Steak Philly + chipotle sauce adds ~120 mg Na. Flavor variant.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 560 | 670 | 280 | 335 |
| Total fat (g) | 18 | 23 | 9 | 11.5 |
| Sat fat (g) | ~1 | ~1 | 0.5 | 0.5 |
| Trans fat (g) | 1 | 1 | 0.5 | 0.5 |
| Chol (mg) | 50 | 105 | 25 | 53 |
| **Sodium (mg)** | **1,105** | **1,555** | **553** | **778** |
| Carbs (g) | 72 | 74 | 36 | 37 |
| Fiber (g) | 3 | 3 | 1.5 | 1.5 |
| Sugars (g) | 16 | 17 | 8 | 8.5 |
| Added sugars (g) | 14 | 15 | 7 | 7.5 |
| Protein (g) | 23 | 40 | 11.5 | 20 |

## Item 4: Cheesy Garlic Steak (NO CHEESE) — HIGH UNCERTAINTY

> PDF does not itemize the extra cheese component. Cheese deduction may undershoot. Recommendation: order Steak Philly no-cheese instead for more reliable numbers.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 570 | 680 | 285 | 340 |
| Sodium (mg) | ~855 | ~1,305 | ~428 | ~653 |
| Protein (g) | 19 | 36 | 9.5 | 18 |

## Item 5: Roast Beef (no cheese by default)

> Highest protein density of the no-cheese-default items. Cold cut, not hot.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 770 | 850 | 385 | 425 |
| Total fat (g) | 30 | 32 | 15 | 16 |
| Sat fat (g) | 7 | 8 | 3.5 | 4 |
| Trans fat (g) | 1 | 1 | 0.5 | 0.5 |
| Chol (mg) | 65 | 100 | 33 | 50 |
| **Sodium (mg)** | **1,530** | **1,950** | **765** | **975** |
| Carbs (g) | 81 | 83 | 40.5 | 41.5 |
| Fiber (g) | 3 | 3 | 1.5 | 1.5 |
| Sugars (g) | 22 | 24 | 11 | 12 |
| Added sugars (g) | 20 | 22 | 10 | 11 |
| Protein (g) | 34 | 49 | 17 | 24.5 |
| K (mg, est.) | ~750 | ~900 | ~375 | ~450 |

## Item 6: Seasoned Steak & Smashed Avocado

> Avocado built-in. Higher fiber (6g vs 3g), better macro balance.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 480 | 590 | 240 | 295 |
| Total fat (g) | 16 | 21 | 8 | 10.5 |
| Sat fat (g) | 3 | 5 | 1.5 | 2.5 |
| Chol (mg) | 30 | 85 | 15 | 43 |
| **Sodium (mg)** | **1,025** | **1,475** | **513** | **738** |
| Carbs (g) | 63 | 65 | 31.5 | 32.5 |
| **Fiber (g)** | **5** | **6** | **2.5** | **3** |
| Sugars (g) | 15 | 17 | 7.5 | 8.5 |
| Added sugars (g) | 15 | 17 | 7.5 | 8.5 |
| Protein (g) | 19 | 36 | 9.5 | 18 |

## Item 7: Seasoned Steak & Fresh Avocado ⭐ AGENT'S BEST OVERALL PICK

> Lowest calories / highest fiber / best protein-per-calorie ratio / no cheese default. Best daily rotation choice by the numbers.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 450 | 560 | 225 | 280 |
| Total fat (g) | 14 | 19 | 7 | 9.5 |
| Sat fat (g) | 2 | 4 | 1 | 2 |
| Chol (mg) | 30 | 85 | 15 | 43 |
| **Sodium (mg)** | **895** | **1,345** | **448** | **673** |
| Carbs (g) | 63 | 65 | 31.5 | 32.5 |
| **Fiber (g)** | **5** | **6** | **2.5** | **3** |
| Sugars (g) | 15 | 17 | 7.5 | 8.5 |
| Added sugars (g) | 15 | 17 | 7.5 | 8.5 |
| Protein (g) | 19 | 36 | 9.5 | 18 |

## Item 8: Big Hot Pastrami ❌ AVOID

> FL single alone exceeds daily Na UL. Double is at 146% of UL. Red across every axis.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 950 | 1,080 | 475 | 540 |
| Total fat (g) | 49 | 59 | 24.5 | 29.5 |
| Sat fat (g) | 14 | 17 | 7 | 8.5 |
| Chol (mg) | 125 | 160 | 63 | 80 |
| **Sodium (mg)** | **2,945** ❌ | **3,415** ❌ | **1,473** | **1,708** |
| Carbs (g) | 76 | 76 | 38 | 38 |
| Fiber (g) | 3 | 3 | 1.5 | 1.5 |
| Added sugars (g) | 14 | 14 | 7 | 7 |
| Protein (g) | 41 | 50 | 20.5 | 25 |

## Item 9: Meatball Marinara (Reference — verified Round 2)

> Highest sat fat in the lineup (tied with pastrami-range). Fat-heavy / carb-heavy / protein-modest.

| Nutrient | FL single | FL double | 6" single | 6" double |
|---|---|---|---|---|
| Calories | 880 | 1,020 | 440 | 510 |
| Total fat (g) | 45 | 54 | 22.5 | 27 |
| Sat fat (g) | 16 | 19 | 8 | 9.5 |
| Chol (mg) | 75 | 95 | 38 | 48 |
| **Sodium (mg)** | **2,015** | **2,445** | **1,008** | **1,223** |
| Carbs (g) | 87 | 96 | 43.5 | 48 |
| Fiber (g) | 7 | 7 | 3.5 | 3.5 |
| Added sugars (g) | 17 | 19 | 8.5 | 9.5 |
| Protein (g) | 27 | 41 | 13.5 | 20.5 |
| K (mg, est.) | ~1,060 | ~1,215 | ~530 | ~608 |

---

## Cross-Item Ranking (Footlong Double, no cheese, Vincent's standard build)

| Rank | Item | Na | SatFat | Protein | Cal | Note |
|---|---|---|---|---|---|---|
| 1 | Seasoned Steak & Fresh Avo ⭐ | 1,345 | 4 | 36 | 560 | Best overall |
| 2 | Steak Philly no-cheese | 1,435 | ~1 | 39 | 680 | Best hot cheesesteak |
| 3 | Seasoned Steak & Smashed Avo | 1,475 | 5 | 36 | 590 | - |
| 4 | Chipotle Philly no-cheese | 1,555 | ~1 | 40 | 670 | Spicy variant |
| 5 | Roast Beef | 1,950 | 8 | 49 | 850 | Highest protein |
| 6 | SOT Teriyaki Chicken | 1,995 | 6 | 46 | 750 | ⚠️ 34g added sugar |
| 7 | Meatball Marinara | 2,445 | 19 | 41 | 1,020 | ⚠️ Fat bomb |
| 8 | Big Hot Pastrami ❌ | 3,415 | 17 | 50 | 1,080 | Skip entirely |

## Decision Rules

**Daily rotation (Na goal priority):**
- Best: Seasoned Steak & Fresh Avocado (any meat level)
- Second: Steak Philly no-cheese (any meat level)
- Third: Chipotle Philly no-cheese (any meat level)

**Protein priority (post-workout, etc.):**
- Roast Beef double (49g protein, 1,950 mg Na) — highest protein within tolerable Na
- SOT Teriyaki Chicken double (46g protein) — but watch sugar

**Sugar-aware days (low added sugar target):**
- Avoid SOT Teriyaki Chicken (34g added sugar FL double)
- Avoid Roast Beef FL double (22g added sugar)
- Best: Steak Philly / Chipotle Philly / Cheesesteaks (15g added sugar range)

**Flavor indulgence day:**
- Meatball Marinara single meat only
- Pair with 48h low-sodium recovery window after

**Always avoid:**
- Big Hot Pastrami (any size)
- Default Cheesesteaks (with cheese)
- Meatball Marinara double meat

## Double Meat Rules

| Item | Double OK? | Reason |
|---|---|---|
| Seasoned Steak & Fresh Avo | ✅ | Na stays under 1,500 |
| Steak Philly no-cheese | ✅ | Na stays at 1,435 |
| Chipotle Philly no-cheese | ✅ | Na 1,555 acceptable |
| Seasoned Steak & Smashed Avo | ✅ | - |
| Roast Beef | ⚠️ | 1,950 Na borderline, not every time |
| SOT Teriyaki Chicken | ⚠️ | Sugar doubles to 34g added |
| Meatball Marinara | ❌ | Fat + Na double-up |
| Big Hot Pastrami | ❌ | Always over UL |

## Hard vs Estimated

- **Hard-sourced (Subway US Nutrition Jan 2026 PDF):** all sandwich rows, individual protein rows, cheese rows, adder rows — calories, fat, sat fat, trans, chol, Na, carb, fiber, sugar, added sugar, protein, %DV
- **Estimated/derived:** Potassium (USDA FoodData Central, ±150 mg uncertainty); Ca/Fe absolute mg (%DV × FDA anchors 1,300 mg / 18 mg)
- **High uncertainty:** Cheesy Garlic Steak cheese-stripped values (PDF doesn't itemize the extra cheese)
- **Floored values:** Cheese-stripped Cheesesteaks sat fat rounds to 0-1g due to PDF whole-gram precision; real values likely 1-2g

## Sources

- Subway US Nutrition Information January 2026: https://www.subway.com/en-us/-/media/northamerica/usa/nutrition/nutritiondocuments/2026/us_nutrition_en_1-2026.pdf
- USDA FoodData Central: https://fdc.nal.usda.gov/
- FDA Daily Value anchors: https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels

## Daily Log Quick-Insert Rows (per agent rubric)

Use these when logging into `daily-log.md`. Columns match the agent's standard table: 食材 / 量 / 热量 / 蛋白 / 碳水 / 脂肪 / 钠 / 钾 / 来源.

| Build | 量 | kcal | 蛋白 | 碳水 | 脂肪 | 钠 | 钾 | 来源 |
|---|---|---|---|---|---|---|---|---|
| Steak Philly no-cheese 6" double | 1份 | 340 | 19.5 | 37 | 13 | 718 | ~425 | knowledge-base (subway_reference) |
| Steak Philly no-cheese FL double | 1份 | 680 | 39 | 74 | 26 | 1,435 | ~850 | knowledge-base |
| Seasoned Steak & Fresh Avo 6" double ⭐ | 1份 | 280 | 18 | 32.5 | 9.5 | 673 | ~425 | knowledge-base |
| Seasoned Steak & Fresh Avo FL double ⭐ | 1份 | 560 | 36 | 65 | 19 | 1,345 | ~850 | knowledge-base |
| Roast Beef 6" double | 1份 | 425 | 24.5 | 41.5 | 16 | 975 | ~450 | knowledge-base |
| SOT Teriyaki Chicken 6" double | 1份 | 375 | 23 | 48 | 10.5 | 998 | ~400 | knowledge-base |
| Meatball Marinara 6" double | 1份 | 510 | 20.5 | 48 | 27 | 1,223 | ~608 | knowledge-base |

> All numbers include Vincent's standard adders (SOT ×2 footlong dose, Subkrunch, Oregano) and the no-cheese deduction where applicable.

## Agent Decision Rules (rubric-aligned)

**Pre-order check (run before confirming a Subway entry):**
1. Project Na sub-total after this meal vs 2300 mg UL. If projected ≥ 80% UL, downgrade to a single 6" or switch to Steak & Fresh Avo.
2. Project sat fat sub-total vs 20 g DV. If projected ≥ 80%, refuse Meatball Marinara double, refuse Roast Beef double.
3. Project added sugar vs 50 g DV. If projected ≥ 60%, refuse SOT Teriyaki Chicken double.
4. Compute Na:K projected ratio. If > 1.2, recommend pairing with avocado/banana/leafy green at next meal.

**Post-meal flag thresholds:**
- Na single-meal ≥ 1,500 mg → 48h low-Na recovery window flagged in daily-log footer.
- Sat fat single-meal ≥ 12 g → fat-bomb flag, recommend lean protein next meal.
- Single-meal protein < 30 g → log warning per agent rubric §每餐蛋白检查.

**Recovery pairings (next 24h after a Na-heavy Subway meal):**
- Avocado (½ → 345 mg K, 5 mg Na — see avocado_reference.md)
- Banana (~422 mg K, 1 mg Na)
- Spinach 100 g cooked (~466 mg K, 79 mg Na)
- Lentils 100 g cooked (~369 mg K, 2 mg Na)
- Plain Greek yogurt 170 g (~240 mg K, 65 mg Na)

## DV Anchors Used

| Nutrient | Daily Value |
|---|---|
| Sodium | 2,300 mg (FDA UL) / 1,500 mg (AHA ideal) |
| Saturated fat | 20 g |
| Fiber | 28 g |
| Added sugar | 50 g |
| Calcium | 1,300 mg |
| Iron | 18 mg |
| Potassium | 4,700 mg |
| Protein | ~100 g (for 70 kg adult) |
