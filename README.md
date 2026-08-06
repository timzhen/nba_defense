# NBA Defensive Scouting Report

A full-stack web app that rates NBA players across five distinct defensive categories, validates those ratings against real historical Defensive Player of the Year (DPOY) voting using a trained machine learning model, and lets users ask an AI chatbot to explain any player's rating using their actual underlying stats.

**Live site:** https://nba-defense.vercel.app

---

## Why this project exists

Traditional defensive stats (blocks, steals) capture only a sliver of what makes someone a good defender. A rim-protecting big, a point-of-attack perimeter defender, and a high-activity disruptor all "defend" in completely different ways, but conventional box scores flatten them into the same handful of numbers.

This project breaks defense into five measurable categories, built from real NBA tracking data, and then tests — using actual machine learning rather than just intuition — whether those categories predict real-world recognition of great defenders.

---

## Features

- **Player Search** — search any current-season NBA player and see their defensive breakdown as a visual scouting report, with percentile rankings and qualitative labels (Elite / Above Average / Average / Below Average / Poor) instead of raw, hard-to-interpret scores.
- **Team Browser** — browse all 30 teams by logo, click into any roster, and click any player to see their full defensive profile inline.
- **DPOY Leaderboard** — a model-generated ranking of this season's most statistically similar players to past DPOY vote-getters, based on a logistic regression model trained on five prior NBA seasons.
- **Ask About This Player (AI chatbot)** — type a natural-language question about any searched player (e.g. *"why is he good at rim protection?"*), and an LLM (Gemini) answers using that player's real underlying stats — not just the calculated score, but the actual blocks, deflections, opponent shooting percentages, etc. that produced it.

---

## The five defensive categories

| Category | Built from |
|---|---|
| Rim Protection | Blocks, opponent points in the paint, defensive rating |
| Shot Contesting | Contested 2PT shots, contested 3PT shots |
| Ball Disruption | Deflections, steals, charges drawn |
| On-Ball Matchup Defense | Opponent FG% and 3PT% allowed in tracked individual matchups |
| Defensive Rebounding | Defensive rebounds, defensive boxouts |

Each underlying stat is min-max normalized to a 0–100 scale (worst player in the league = 0, best = 100) before being combined into a weighted category score. Category scores are then converted to **percentile rank** for display, since a raw normalized score doesn't always map intuitively to "good" or "bad" — a player can score a 37 on a skewed distribution while still being solidly above average. Percentile rank fixes that ambiguity.

---

## The data

Data comes from three `nba_api` endpoints, pulled for **seven NBA seasons**: 2015-16, 2016-17, 2018-19, 2019-20, 2022-23, 2023-24, and 2025-26.

- `LeagueDashPlayerStats` (Defense measure type) — blocks, steals, defensive rating, opponent points in the paint
- `LeagueHustleStatsPlayer` — contested shots, deflections, charges drawn, boxouts
- `LeagueSeasonMatchups` — individual defender-vs-offensive-player matchup data, aggregated per defender

Across all seasons, this totals **over 2,100 player-season rows** and several hundred thousand raw matchup-level rows before aggregation. Each season's three data sources are merged on player ID, cleaned, filtered for a minimum sample size (40+ games played, 500+ minutes), normalized, and scored.

### Missing data — what's missing and why

Not all "missing" data is the same, and this project treats each case differently rather than blindly filling gaps:

**Historical tracking gaps (2015-16, 2016-17).** The NBA didn't track hustle stats (boxouts, some deflection data) as comprehensively in these earlier seasons. Rather than fabricate values for stats that simply didn't exist yet, these two seasons are excluded from the ML model's training data — they're still shown for players where the data does exist, but not used to validate the model.

**Small-sample noise (on-ball matchup defense).** Individual matchup tracking data is sparse for some players — someone might only have a handful of tracked defensive possessions against a specific opponent, making their "opponent FG% allowed" wildly unreliable (a single make/miss swings the percentage enormously). Any player with fewer than 100 total tracked matchup possessions has their on-ball matchup score set to missing (`null`) rather than an artificially extreme number. The frontend displays this as "N/A" instead of a misleading score.

**API-side gaps.** `nba_api` — the unofficial Python wrapper this project relies on for NBA.com's internal stats service — is not a stable, documented, official API. Over the course of building this project:
- Several historical seasons intermittently returned completely empty responses from the same endpoint call that worked fine moments later or for other seasons, with no error thrown — just silently empty data.
- A specific player (Stephen Curry, 2025-26) was found to be excluded purely because his games-played/minutes fell just below an earlier, stricter sample-size threshold — not a data availability issue, but a filtering choice that got revisited once discovered.
- Package updates were required mid-project after discovering `nba_api`'s older versions sent outdated request headers that NBA.com's servers had started silently rejecting.

Where a season could not be reliably fetched even after multiple retries, it was simply excluded from that run rather than faked — the pipeline logs exactly which seasons succeeded and which need retrying, and caches successful pulls locally so repeated runs don't re-hit a flaky external service unnecessarily.

---

## The ML validation

A logistic regression model was trained on five clean historical seasons (2018-19 through 2023-24, plus 2019-20) to test whether the five category scores predict whether a player received real Defensive Player of the Year votes.

**Findings:** Rim Protection and Ball Disruption emerged as the strongest, most consistent predictors of DPOY recognition — a pattern that held steady and even strengthened as more historical seasons were added to training. Shot Contesting and On-Ball Matchup Defense showed meaningfully weaker correlation with actual award recognition.

**Honest limitations:** The training set is small (only ~35 total DPOY vote recipients across all seasons combined, against a much larger pool of non-recipients), which limits how finely the model can distinguish between "very good" and "elite" defenders — predicted probabilities cluster toward the extremes rather than forming a smooth distribution. For the live DPOY Leaderboard feature, the deployed model is trained *excluding* the current season entirely, to avoid the model being evaluated on data it was trained on.

---

## Tech stack

| Layer | Technology |
|---|---|
| Data pipeline | Python, pandas, `nba_api` |
| ML | scikit-learn (logistic regression) |
| Backend | FastAPI, deployed on Railway |
| Frontend | React (Vite), deployed on Vercel |
| AI chatbot | Google Gemini API |

---

## Running locally

**Backend**
```bash
cd nba-defense-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create a .env file with GEMINI_API_KEY=your_key_here
uvicorn main:app --reload
```

**Frontend**
```bash
cd nba-defense-frontend
npm install
npm run dev
```

**Data pipeline** (only needed to regenerate the underlying data)
```bash
cd pipeline
python build_defense_scores.py
```

---

## What I'd improve with more time

- Retrain the ML model on a larger, more balanced set of DPOY examples for smoother, more differentiated probability output
- Recover the handful of historical seasons that were never successfully pulled due to `nba_api` reliability issues
- Add historical season comparison to the player search view, not just current-season data
