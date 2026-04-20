---
id: movement-pattern-programming-variable-locations
title: "Movement-pattern-based programming for training across variable gym locations"
concept: Movement-pattern-based programming for training across variable gym locations
author: Dan John, Mike Boyle, Schoenfeld, Fonseca et al.
source_title: Multiple sources (web research compilation)
source_date: 2014-2025
logged: 2026-04-09
tags: [movement-patterns, programming, variable-equipment, exercise-equivalence, RPE]
related: [fitness-agent-design]
status: confirmed
last_modified: 2026-04-15
---

# Movement-Pattern Programming for Variable Locations

## Core Patterns (6-8)
| Pattern | Sub-category | Goal Alignment |
|---|---|---|
| Horizontal Push | Push-up, bench variants | Upper hypertrophy |
| Horizontal Pull | Row variants | Upper hypertrophy, climbing balance |
| Vertical Push | Overhead press variants | Upper hypertrophy |
| Vertical Pull | Pull-up, pulldown variants | Climbing-specific |
| Hip Hinge | Deadlift, swing variants | Carry goal, riding hip |
| Knee Dominant | Squat, lunge, step-up | Pistol squat goal, riding |
| Loaded Carry | Farmer, bear hug, overhead | Carry goal directly |
| Rotation/Anti-rotation | Pallof, chops, mace | Riding trunk stability, climbing |

## Exercise Equivalence Map (4 Locations)
| Pattern | Home (Balcony) | Climbing Gym | Full Gym | University Gym |
|---|---|---|---|---|
| H-Push | Sandbag floor press, DB press | Plate floor press, push-up variations | DB/barbell bench | Machine chest press, cable fly, bench |
| H-Pull | Band row, sandbag bent row | DB row, band pull-apart | Cable row, DB row | Seated row machine, chest-supported row |
| V-Push | Mace press, DB press standing | DB overhead press | Barbell OHP | Shoulder press machine, landmine press |
| V-Pull | Pull-up bar, band pulldown | Pull-up area (weighted) | Lat pulldown, pull-ups | Every pulldown/pull-up variant |
| Hinge | Sandbag RDL, sandbag good morning | Plate RDL, band pull-through | Barbell RDL/deadlift | Hex bar DL, GHD, cable pull-through |
| Knee Dom | Sandbag goblet squat, pistol progressions | Box pistol squat, plate goblet squat | Barbell squat, BSS | Leg press, hack squat, leg extension |
| Carry | Sandbag bear hug carry (45kg) | Plate carry, DB farmer carry | DB/barbell carry | Trap bar carry, sled push |
| Rotation | Mace 360s, band rotation | Band Pallof, plate chop | Cable woodchop | Every cable/machine option |

## Tracking Progressive Overload
- Track by pattern, not exercise. RPE as universal currency
- Log: pattern | exercise | load | reps × sets | RPE | location
- Same pattern, same RPE target, increase volume or load over weeks
- Research (Schoenfeld 2010, Fonseca 2014): exercise variation within a pattern produces comparable or superior hypertrophy to fixed-exercise programs

## Optimal Storage Structure for AI Agent
```yaml
movement_patterns:
  hip_hinge:
    locations:
      home: [{exercise: "Sandbag RDL", load_range: "45kg", rep_range: "8-12"}]
      climbing_gym: [{exercise: "Plate RDL", load_range: "20-40kg", rep_range: "8-12"}]
      full_gym: [{exercise: "Barbell RDL", load_range: "40-80kg", rep_range: "6-10"}]
      university: [{exercise: "Hex Bar DL", load_range: "60-100kg", rep_range: "5-8"}]
    track_by: RPE
    weekly_target: {sets: 10-14, intensity: "RPE 7-9"}
```
