---
id: sleep-regularity-fitness-readiness
title: "Sleep Regularity Integration into Fitness Readiness Systems"
concept: Sleep Regularity Integration into Fitness Readiness Systems
author: compiled from multiple sources (Phillips 2017, Windred 2023, Jankowski 2017, Zuraikat 2024, Chaput 2025, Hisler 2024)
source_title:
  - "Measuring sleep regularity: theoretical properties and practical usage of existing metrics (Windred et al., SLEEP 2021)"
  - "Sleep regularity is a stronger predictor of mortality risk than sleep duration (Zuraikat et al., SLEEP 2024)"
  - "Sleep Regularity and Mortality: A Prospective Analysis in the UK Biobank (Windred et al., eLife 2023)"
  - "Effects of sleep deprivation on heart rate variability: a systematic review and meta-analysis (Frontiers in Neurology 2025)"
  - "Effects of sleep deprivation on sports performance and perceived exertion (Frontiers in Physiology 2025)"
  - "Social jet lag impairs exercise volume and attenuates physiological and metabolic adaptations (J Appl Physiol 2024)"
  - "The importance of sleep regularity: NSF consensus statement (Sleep Health 2023)"
  - "Heart rate variability rebound following exposure to persistent and repetitive sleep restriction (PMC 2019)"
source_date: 2019-2025
logged: 2026-04-09
tags: [sleep-regularity, readiness, HRV, performance, computational-model, social-jet-lag, SRI, fitness-agent]
related: [fitness-agent, readiness-gate, horsys-wellness]
status: confirmed
last_modified: 2026-04-15
---

# Sleep Regularity Integration into Fitness Readiness Systems

## 1. Sleep Regularity and Next-Day Exercise Performance

### Key Finding: Regularity Matters Independent of Duration
Sleep regularity is a stronger predictor of health outcomes than sleep duration (Zuraikat 2024). Irregular sleep timing, even with adequate total hours, impairs training adaptation and performance.

### Effect Sizes: Sleep Deprivation on Performance (Chaput 2025 meta-analysis)
| Domain | SMD (Cohen's d) | Direction |
|---|---|---|
| Aerobic endurance | -0.66 | Impaired |
| Explosive power | -0.63 | Impaired |
| Speed | -0.52 | Impaired |
| RPE accuracy | +0.39 | Inflated (perceive effort as harder) |
| Maximal force | -0.35 | Impaired |
| Skill control | -0.87 | Most impaired |

Note: These are total deprivation effects. Partial restriction (irregular timing) produces smaller but cumulative effects.

### Early vs Late Sleep Deprivation
- **Early-night loss** (delayed bedtime): Reduces explosive power, maximal force, speed, RPE
- **Late-night loss** (early wake): Reduces speed, skill control, RPE
- Implication: For strength training, delayed bedtime is worse; for skill/coordination work, early waking is worse

### Social Jet Lag and Training Adaptation (Aoyama et al., J Appl Physiol 2024)
Mice with induced social jet lag (weekly schedule shifts) showed:
- Decreased voluntary exercise volume
- Blunted improvements in exercise performance
- Reduced mitochondrial content in quadriceps
- Impaired glucose tolerance (partially restored by exercise)
- Higher injury risk during training periods

**Practical threshold**: Social jet lag > 2 hours consistently associated with metabolic impairment and reduced training adaptation.

---

## 2. Sleep Regularity and HRV Interaction

### Direct HRV Impact (Frontiers in Neurology 2025 meta-analysis, 11 RCTs, n=549)
| HRV Metric | SMD after sleep deprivation | Interpretation |
|---|---|---|
| RMSSD | -0.24 (95% CI: -0.47 to -0.00) | Small but significant parasympathetic suppression |
| LF power | Increased | Sympathetic activation |
| LF/HF ratio | Increased | Autonomic imbalance toward sympathetic dominance |

The -0.24 RMSSD effect is modest for acute deprivation, but **chronic irregularity produces cumulative autonomic disruption** that compounds over days.

### Irregular Sleep Pattern Coupling
People with irregular sleep patterns show stronger sleep-HRV coupling, meaning HRV becomes more volatile and reactive. This suggests variability in timing, not just duration, is the bigger autonomic disruptor.

### Clinical Evidence
- Moderately irregular sleep doubles the risk of clinical cardiac events within 6 months (OHSU 2025)
- A consistent 7.5h schedule outperforms a 6h weekday / 9h weekend pattern for HRV

### HRV Recovery Timeline After Schedule Normalization
| Disruption | Recovery to baseline |
|---|---|
| Single night of total sleep deprivation | >1 night (does NOT recover in one night) |
| Multiple nights at ~50% sleep | Minimum 3 nights of normal sleep |
| Shift work (2-7 consecutive night shifts) | Recovery days needed roughly equal to disruption days |
| Chronic irregular schedule (weeks) | Estimated 1-2 weeks of consistent timing |

**Key insight for readiness gate**: After a period of irregular sleep, HRV readings remain suppressed for 2-3 days even after returning to normal schedule. The readiness gate should maintain a "recovery penalty" during this lag period.

---

## 3. Computational Models for Sleep Regularity

### Model A: Standard Deviation of Sleep Midpoint (Simplest, Recommended for Text Input)

```
For each night i, compute:
  midpoint_i = bedtime_i + (waketime_i - bedtime_i) / 2

Over 7 days:
  SD_midpoint = stdev(midpoint_1 ... midpoint_7)

Score interpretation:
  SD < 30 min  -> Regular (green)
  SD 30-60 min -> Mildly irregular (yellow)
  SD 60-90 min -> Moderately irregular (orange)
  SD > 90 min  -> Highly irregular (red)
```

**Advantages**: Dead simple, computable from self-reported bed/wake times, validated in SWAN study and multiple cohorts.

**Also compute separately**:
- `SD_bedtime` = stdev of bedtimes (captures schedule drift)
- `SD_waketime` = stdev of wake times (captures alarm vs free-wake variation)
- `SD_duration` = stdev of sleep durations (captures quantity inconsistency)

### Model B: Social Jet Lag (SJL) -- For Weekly Pattern Detection

```
MSW = mean midpoint of sleep on workdays (e.g., Mon-Fri)
MSF = mean midpoint of sleep on free days (e.g., Sat-Sun)

SJL = |MSF - MSW|

Sleep-corrected version (Jankowski 2017):
  SJL_sc = |sleep_onset_free - sleep_onset_work|

Score interpretation:
  SJL < 1.0 h  -> Minimal jet lag (green)
  SJL 1.0-2.0 h -> Moderate (yellow)
  SJL > 2.0 h  -> Severe, expect impaired adaptation (red)
```

### Model C: Simplified SRI (Sleep Regularity Index) for Text Input

The full SRI uses 30-second epoch data from wearables. For self-reported data, use this approximation:

```
For each consecutive day pair (i, i+1):
  overlap_i = hours where sleep windows intersect / max(duration_i, duration_i+1)

SRI_approx = mean(overlap_1 ... overlap_6) * 100

Where sleep window intersection is computed as:
  overlap_start = max(bedtime_i, bedtime_i+1)
  overlap_end = min(waketime_i, waketime_i+1)
  intersection = max(0, overlap_end - overlap_start)

Score: 0-100 scale
  > 85 -> Regular
  70-85 -> Moderate
  < 70 -> Irregular
```

### Recommended Composite for Readiness Gate

Use Model A (SD_midpoint) as primary metric. It requires only bed/wake times, is trivially computable, and has the strongest research backing for self-report data. Add Model B (SJL) as a weekly pattern detector.

```python
def sleep_regularity_score(bed_wake_pairs_7d):
    """
    Input: list of 7 (bedtime, waketime) tuples in decimal hours
           e.g., (23.5, 7.0) = 11:30 PM to 7:00 AM
    Returns: regularity_score (0-100), penalty_factor (0.0-1.0)
    """
    midpoints = []
    for bed, wake in bed_wake_pairs_7d:
        # Handle overnight: if wake < bed, add 24
        if wake < bed:
            wake += 24
        mid = bed + (wake - bed) / 2
        midpoints.append(mid)
    
    sd_mid = stdev(midpoints)  # in hours
    
    # Convert SD to 0-100 score (0 min SD = 100, 2h SD = 0)
    score = max(0, min(100, 100 - (sd_mid / 2.0) * 100))
    
    # Penalty factor for readiness gate (1.0 = no penalty)
    if sd_mid < 0.5:      # < 30 min
        penalty = 1.0
    elif sd_mid < 1.0:    # 30-60 min
        penalty = 0.90
    elif sd_mid < 1.5:    # 60-90 min
        penalty = 0.75
    else:                  # > 90 min
        penalty = 0.60
    
    return score, penalty
```

---

## 4. Thresholds for the Readiness System

### Evidence-Based Cutoffs

| Metric | Green (train normally) | Yellow (reduce volume 10-15%) | Orange (reduce intensity 20-30%) | Red (recovery day) |
|---|---|---|---|---|
| SD midpoint (7d) | < 30 min | 30-60 min | 60-90 min | > 90 min |
| Social jet lag | < 1.0 h | 1.0-1.5 h | 1.5-2.0 h | > 2.0 h |
| SRI approx | > 85 | 70-85 | 55-70 | < 55 |
| Consecutive irregular nights | 0-1 | 2 | 3-4 | 5+ |

### Interaction with Existing Readiness Metrics

Sleep regularity should **multiply** (not add to) the existing readiness score:

```
final_readiness = base_readiness(HRV, RHR, stress, sleep_hours) * sleep_regularity_penalty

Where sleep_regularity_penalty ranges from 0.60 to 1.00
```

Rationale: Irregular sleep suppresses HRV readings, meaning the HRV input is already partially capturing the effect. A multiplicative penalty avoids double-counting while still flagging the schedule disruption that HRV alone may not fully reflect (especially in the first 1-2 days before HRV catches up).

### Recovery Signal Logic

Issue a "recovery signal" when ANY of:
1. SD_midpoint > 60 min over past 7 days
2. Social jet lag > 2.0 hours this week
3. Sleep midpoint shifted > 2 hours from prior 3-day average (acute disruption)
4. 3+ consecutive nights with bedtime varying > 1 hour from personal average

### Post-Irregularity Recovery Ramp

After returning to regular schedule:
- Day 1-2: Maintain recovery penalty (HRV still suppressed)
- Day 3-4: Reduce penalty by 50%
- Day 5+: Clear penalty if SD_midpoint has normalized

```
days_since_regular = count consecutive days with |midpoint - avg_midpoint| < 30 min
recovery_multiplier = min(1.0, 0.6 + (days_since_regular * 0.1))
```

### Mortality/Health Context for Threshold Validation

From UK Biobank (n=60,977, Windred et al. 2023):
- SRI 5th percentile (score ~41): HR 1.53 for all-cause mortality
- SRI 95th percentile (score ~75): HR 0.90
- Median SRI in healthy population: 81

From Zuraikat et al. 2024:
- Most regular quintile (SRI 80-100): HR 0.74 for mortality (fully adjusted)
- Most irregular quintile (SRI bottom 20%): Reference group
- Sleep regularity was a stronger mortality predictor than sleep duration

These population-level thresholds support the readiness gate cutoffs: an SRI-equivalent below ~70 (our "orange" zone) corresponds to meaningfully elevated health risk and is where training adaptation begins to degrade.

---

## Implementation Notes for Fitness Agent

1. **Data collection**: Ask for bed/wake times for past 7 nights. Can be approximate ("around 11:30" is fine).
2. **Minimum data**: Need at least 5 of 7 nights. Fewer than 5 = insufficient data, default to neutral penalty (0.90).
3. **Time parsing**: Handle "midnight" = 0:00, "1 AM" = 1:00, etc. All times should be converted to decimal hours.
4. **Weighting**: Recent nights matter more. Optional: weight last 3 nights at 2x in SD calculation.
5. **Display**: Show the regularity score alongside HRV/RHR/stress in the readiness dashboard. Use the green/yellow/orange/red scheme.
6. **Narrative**: When penalty is active, explain WHY: "Your sleep schedule has shifted by ~1.5 hours over the past week. This can suppress HRV and reduce training adaptation. Consider dialing back volume today."
