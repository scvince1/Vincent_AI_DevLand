---
id: sleep-regularity-index-circadian-consistency
title: "Sleep Regularity Index and Circadian Consistency for Athletic Recovery"
concept: Sleep Regularity Index and Circadian Consistency for Athletic Recovery
author: [compiled from multiple sources]
source_title:
  - "Sleep regularity is a stronger predictor of mortality risk than sleep duration (Windred et al., SLEEP 2024)"
  - "Sleep Regularity and Mortality: A Prospective Analysis in the UK Biobank (Zuraikat et al., eLife 2023)"
  - "The importance of sleep regularity: NSF consensus statement (Gruber et al., Sleep Health 2023)"
  - "Social jet lag impairs exercise volume and attenuates physiological adaptations (J Appl Physiol 2024)"
  - "Social jetlag alters markers of exercise-induced mitochondrial adaptations (npj Biological Timing and Sleep 2024)"
  - "The effect of acute sleep deprivation on skeletal muscle protein synthesis (Lamon et al., Physiol Reports 2021)"
  - "Circadian Rhythm Sleep Disturbances in Young Adult Athletes (Brain Sciences 2024)"
  - "Toward a Standardized Framework for Assessing Athletes' Sleep (Curr Sleep Med Rep 2026)"
  - "Sleep Regularity and Predictors in Elite Team Sport Athletes (Sports Med Open 2022)"
source_date: 2021-2026
logged: 2026-04-09
tags: [sleep, regularity, circadian, recovery, HRV, readiness, SRI, social-jetlag, testosterone, muscle-recovery]
related: [fitness-agent, readiness-gate]
status: confirmed
last_modified: 2026-04-15
---

# Sleep Regularity Index and Circadian Consistency for Athletic Recovery

## 1. Sleep Regularity Index (SRI) -- Definition and Calculation

### What It Measures
The SRI quantifies the day-to-day consistency of sleep-wake patterns. It is defined as **the probability that an individual is in the same state (asleep or awake) at any two time points 24 hours apart**.

### Formula (Simplified)
For each epoch (e.g., every 30 seconds or every hour) across all monitored days:

```
SRI = (200 / (M * N)) * SUM[ delta(s[i,j], s[i+1,j]) ] - 100
```

Where:
- M = number of epochs per day
- N = number of day-pairs
- s[i,j] = state (0=sleep, 1=wake) at epoch j on day i
- delta = 1 if same state on consecutive days, 0 otherwise

**Scale:** 0 (completely random) to 100 (perfectly regular).

### Simplified Self-Report Calculation
Without epoch-level data, a practical proxy:
- For each hour of the day (24 bins), record whether the person was asleep or awake
- Compare each hour across consecutive days
- SRI = percentage of hours where the state matched across day-pairs

### Population Distribution and Thresholds

| Percentile | SRI Score | Interpretation |
|-----------|-----------|----------------|
| 5th       | ~41       | Very irregular -- high risk |
| 25th      | ~58       | Below average |
| 50th (median) | ~60  | Population average |
| 75th      | ~72       | Good regularity |
| 95th      | ~75-80    | Very regular |
| Ideal     | 85+       | Excellent (hard to achieve without intention) |

**Key cutoff from UK Biobank (n=60,977):** Bottom quintile SRI < 71.6 was associated with significantly higher mortality. Top four quintiles (SRI 71.6-98.5) showed 20-48% lower all-cause mortality.

**Practical target for an agent:** SRI >= 75 = good; SRI 60-74 = needs improvement; SRI < 60 = red flag.

## 2. Sleep Regularity vs Health and Performance Outcomes

### Mortality (UK Biobank, n=88,975)
- SRI at 5th percentile (41): HR 1.53 for all-cause mortality (vs median)
- SRI at 95th percentile (75): HR 0.90 for all-cause mortality
- **Sleep regularity was a stronger predictor of mortality than sleep duration**
- Top 4 SRI quintiles vs bottom: 22-57% lower cardiometabolic mortality, 16-39% lower cancer mortality

### Hormonal and Muscle Recovery
Sleep deprivation (proxy for disruption) produces:
- **Testosterone decreased 24%** (acute deprivation study, Lamon et al.)
- **Cortisol increased 21%**
- **Muscle protein synthesis decreased 18%**
- Creates "anabolic resistant" phenotype: reduced MPS even with adequate protein intake
- Shift from anabolic (testosterone/IGF-1 driven) to catabolic (cortisol driven) environment

### Social Jetlag and Exercise Adaptation (2024 Animal Model)
- 6 weeks of circadian disruption (social jetlag protocol):
  - Significant weight gain
  - Higher fasting blood glucose
  - Impaired glucose tolerance
  - Attenuated exercise-induced mitochondrial adaptations in heart tissue
  - Reduced voluntary exercise volume

### HRV and Cardiovascular
- Irregular sleep timing associated with: hypertension, elevated inflammatory markers, reduced HRV
- Sleep variability mediates the relationship between poor sleep and daytime sleepiness/fatigue
- Higher HRV correlates with better parasympathetic recovery; irregular sleep suppresses this

### Mental Health (2024-2025 Studies)
- Moderate and high sleep irregularity associated with increased depression and anxiety risk
- Effects independent of total sleep duration
- Increased risk of type 2 diabetes even with recommended sleep duration if timing is irregular

## 3. Practical Tracking Methods (Self-Report, No Wearable)

### Minimum Viable Tracking for the Agent
The agent needs only two data points per day to compute a useful regularity metric:
1. **Bedtime** (lights out / intent to sleep)
2. **Wake time** (final awakening)

### Derived Metrics from Self-Report

| Metric | Calculation | Threshold |
|--------|-------------|-----------|
| **Sleep midpoint SD** | SD of (bedtime + wake_time) / 2 over 7-14 days | < 30 min = good; > 60 min = poor |
| **Bedtime SD** | SD of bedtime over 7-14 days | < 30 min = good; > 45 min = flag; > 60 min = red |
| **Wake time SD** | SD of wake time over 7-14 days | Same thresholds |
| **Social jetlag** | |avg weekend midpoint - avg weekday midpoint| | < 1 hr = good; > 2 hr = significant disruption |
| **Simplified SRI proxy** | See below | >= 75 = good |

### Simplified SRI Proxy for Self-Report
Divide the day into 24 one-hour bins. For each day-pair:
- Mark each bin as sleep or wake based on reported bed/wake times
- Count matching bins across consecutive days
- SRI_proxy = (matching_bins / 24) * 100, averaged over all day-pairs in window

**Example:** Bed 23:00, wake 07:00 vs bed 00:30, wake 08:00 -- differs in bins 23:00, 00:00, 07:00, 08:00 = 4 mismatches = SRI_proxy = (20/24)*100 = 83.

### Professional Sports Thresholds (from standardized framework, 2026)
- **Sleep onset SD > 60 min** over monitoring block: shift session timing, activate bedtime reminder
- **Sleep onset SD > 45-60 min** over 2 weeks: intervention from coaching staff
- **Sleep onset latency > 30 min** on multiple nights: sleep hygiene coaching triggered

### Phone-Based Tracking (No Wearable)
- Apple Health sleep tracking uses phone accelerometer; scores bedtime consistency (30 points of 100) based on last 13 nights
- Apps like Sleep Cycle, SleepScore work from nightstand using sound/motion
- RISE app specifically tracks sleep debt and circadian alignment
- Manual logging (simplest): just record bed/wake times in the agent; agent computes all metrics

## 4. Circadian Disruption Markers (Beyond Timing)

### Observable Self-Report Signals

| Signal | What It Indicates | How to Track |
|--------|-------------------|--------------|
| **Late-night alertness** (feeling wide awake past midnight) | Delayed circadian phase; possible evening chronotype misalignment | Self-report: "Were you alert/energetic after 23:00?" |
| **Morning grogginess > 30 min** | Sleep inertia amplified by circadian misalignment | Self-report: "How long until you felt fully awake?" |
| **Weekend sleep-in > 2 hours** | Social jetlag; biological clock mismatch | Computed from bed/wake data |
| **Appetite timing shifts** | Late-night hunger, no morning appetite | Self-report flag |
| **GI disturbance** | Circadian disruption affects gut motility | Self-report flag |
| **Difficulty falling asleep at intended bedtime** | Phase delay; bedtime earlier than biological night | Sleep onset latency self-report |
| **Daytime sleepiness 13:00-16:00** | Normal dip, but excessive = debt or misalignment | Subjective rating |
| **Mood/irritability in AM** | Cortisol rhythm disruption | Self-report |

### Chronotype Assessment
The Morningness-Eveningness Questionnaire (MEQ) is the gold standard for self-assessed chronotype. Key insight: **misalignment between chronotype and actual sleep schedule is more damaging than the chronotype itself**. An evening-type person forced into early schedules accumulates chronic circadian debt.

### Red Flag Combinations for the Agent
Flag readiness as "compromised" if 2+ of these co-occur:
1. Bedtime SD > 60 min over past 7 days
2. Self-reported late-night alertness on 3+ of past 7 nights
3. Morning grogginess > 30 min on 3+ days
4. Weekend sleep midpoint > 2 hr later than weekday
5. Sleep onset latency > 30 min on 3+ nights

### Athlete-Specific Considerations
- Early morning training forces wake times that may conflict with natural chronotype
- Evening competition shifts bedtime late, creating acute social jetlag
- Travel across time zones compounds the effect
- Recommendation: maintain sleep timing within +/- 30 min on non-training days relative to training days

## 5. Implementation Notes for Fitness Agent

### Data Collection (Minimum)
Each day, capture:
- Bedtime (HH:MM)
- Wake time (HH:MM)
- Sleep quality (1-5 subjective)
- Optional flags: late-night alertness (Y/N), morning grogginess duration (min), sleep onset latency (min)

### Computed Metrics (Rolling 7-day and 14-day Windows)
- Sleep midpoint and its SD
- Bedtime SD and wake time SD
- Social jetlag (weekday vs weekend midpoint delta)
- Simplified SRI proxy
- Trend direction (improving/degrading/stable)

### Readiness Gate Integration
Current readiness factors: sleep duration, sleep quality, training load, soreness.
**Add:** Sleep regularity score (from SRI proxy or timing SD).

Suggested weighting for readiness:
- Sleep duration: 25%
- Sleep quality: 15%
- **Sleep regularity: 20%** (new)
- Training load / recovery balance: 25%
- Soreness / subjective readiness: 15%

### Alert Triggers
- SRI proxy drops below 70 for 7+ days: "Your sleep timing has been inconsistent. This may reduce recovery quality."
- Bedtime SD > 60 min: "Your bedtime has varied by over an hour. Try anchoring to a consistent wind-down time."
- Social jetlag > 2 hr: "Weekend sleep shift detected. This creates a jet-lag-like effect on Monday recovery."
- 3+ circadian disruption flags co-occurring: "Multiple signs of circadian misalignment. Consider prioritizing schedule consistency over sleep duration."
