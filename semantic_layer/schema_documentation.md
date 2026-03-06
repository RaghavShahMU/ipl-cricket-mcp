# IPL Cricket Semantic Layer Documentation

This document describes the semantic layer for the IPL ball-by-ball dataset. It is intended to help the AI understand the schema, entities, and metrics.

## Dataset Overview

The dataset is stored in a table named `balls`. Each row represents a single delivery event in an IPL match.

### Grain
- **One row per delivery event.**
- Illegal deliveries (wides, no-balls) are included. Multiple rows may share the same `over` and `ball` values because illegal deliveries don't advance the ball count in an over.

### Primary Key
- `column00`: Unique row identifier.

### Chronological Ordering
- `ball_no`: Determines the sequence within an innings. Note that illegal deliveries might result in repeating ball numbers if not handled carefully.

## Core Table: `balls`

### Key Columns

| Column | Type | Description |
| :--- | :--- | :--- |
| `match_id` | BIGINT | Unique identifier for each match. |
| `date` | DATE | Match date (YYYY-MM-DD). |
| `season` | VARCHAR | IPL season identifier (e.g., '2007/08' is 2008, '2011' is 2011). |
| `innings` | BIGINT | 1 or 2 (Super Overs: 3-6). |
| `batting_team` | VARCHAR | Team batting. |
| `bowling_team` | VARCHAR | Team bowling. |
| `over` | BIGINT | 0-indexed over (0-19). |
| `ball` | BIGINT | Ball index within the over. |
| `ball_no` | DOUBLE | Chronological order (e.g., 0.1, 0.2). |
| `batter` | VARCHAR | Striker facing the delivery. |
| `bowler` | VARCHAR | Bowler delivering the ball. |
| `valid_ball` | BIGINT | 1 for legal, 0 for illegal (wides, no-balls). |
| `runs_batter` | BIGINT | Runs off the bat. |
| `runs_extras` | BIGINT | Runs from extras (wides, etc.). |
| `runs_total` | BIGINT | Total runs on the delivery (`runs_batter` + `runs_extras`). |
| `runs_bowler` | BIGINT | Runs charged to the bowler. |
| `wicket_kind` | VARCHAR | Type of dismissal (e.g., 'caught', 'bowled'). |
| `player_out` | VARCHAR | Player dismissed. |
| `venue` | VARCHAR | Stadium name. |
| `city` | VARCHAR | City of the match. |

## Metrics Definitions

| Metric | Definition |
| :--- | :--- |
| **Powerplay** | `over` between 0 and 5 inclusive (Overs 1-6). |
| **Middle Overs** | `over` between 6 and 14 inclusive (Overs 7-15). |
| **Death Overs** | `over` between 15 and 19 inclusive (Overs 16-20). |
| **Strike Rate** | `(SUM(runs_batter) / SUM(balls_faced)) * 100` |
| **Economy Rate** | `SUM(runs_bowler) / (SUM(valid_ball) / 6.0)` |
| **Dot Ball** | `runs_total = 0 AND valid_ball = 1` |
| **Boundary** | `runs_batter IN (4, 6)` |

## Entity Resolution Strategy

The AI should resolve variations in names for players, teams, and venues using fuzzy matching or predefined mappings.

### Teams
- Use full names where possible.
- Mapping examples: "KKR" -> "Kolkata Knight Riders", "MI" -> "Mumbai Indians".

### Players
- Standardize names (e.g., "V Kohli" for "Virat Kohli").

## Query Rules
- Only generate `SELECT` queries.
- Do not attempt `INSERT`, `UPDATE`, or `DELETE`.
- Always verify metrics against the definitions above.
