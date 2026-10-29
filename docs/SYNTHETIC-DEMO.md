# How the synthetic scouting demo works

Open the app and choose **Synthetic demo** under **Data source** in the navigation. The demo opens
by default. The original real records are available under **Real records**.

## Try it

1. Discover players. There are 160 fictional profiles across four fictional leagues and ten positions.
Use name, position, age, foot, value and status filters; sort or change the table/card layout.
2. Open a profile. All five metrics are populated. The radar compares the player with the four
players in that league and position; the gray shape is the cohort median. Raw values sit below.
3. Select **Find similar players**. Five alternatives appear with similarity scores. Follow any
result to compare another complete profile.
4. Save a player with the bookmark. The shortlist persists in this browser. Real and synthetic
saves are kept but shown only in their selected source view.
5. Open **Eligibility checker**. In demo mode, select **Documented parent**, **Missing evidence** or
**Association switch**, then run the preliminary check. Each example exercises a different result.
6. Select **Export report** on a profile. The one-page PDF prominently identifies synthetic data.

Example profile: http://127.0.0.1:8000/players/synthetic-v1-001

## Where the data comes from

`scripts/seed_synthetic.py` creates the records offline. A fixed random seed, 20261028, makes every
run reproducible. It creates 40 league/position groups with four players each. All names, clubs,
ages, feet, heights, values, contracts, statuses and statistics are fictional demo facts. Names may
coincidentally resemble a real person's name; these profiles do not describe those people.

The metrics start from position-specific templates. Strikers tend to score more, defenders tend
to win more aerial duels, and midfielders/wingers have stronger passing or carrying profiles.
Shared quality and creativity factors plus bounded variation give the generated values structure.
These are illustrative assumptions, not a statistically validated football simulation.

Regenerate safely from the project root:

```sh
.venv/bin/python -m scripts.seed_synthetic
```

This updates only reserved `synthetic-v1-` IDs and never fills invented stats on real profiles.
The standard `scripts.seed_data` command also creates the demo alongside the maintained real roster.
Records persist in SQLite; the web interface calls the normal API, not a mock response.

## What the numbers mean

| Metric | Unit |
| --- | --- |
| Goals | Goals per 90 minutes |
| Key passes | Passes leading to a shot per 90 minutes |
| Progressive carries | Progressive carries per 90 minutes |
| Tackles won | Tackles won per 90 minutes |
| Aerial duels | Percentage won, 0–100 |

The first four are normalized to a full match. A value of 0.30 goals/90 describes a rate of roughly
three goals per ten full matches; it is not a forecast. The fifth is a percentage rather than a rate.

## Radar chart

Different units cannot be plotted as directly comparable raw lengths. Each metric becomes a
percentile rank inside the complete same-league/position cohort, using midranks for ties. For four
players, distinct ranks are 12.5, 37.5, 62.5 and 87.5. The chart spans 0–100 and plots the cohort's
median on the same scale. The underlying numbers remain visible below the chart.

A high percentile means a higher recorded value for that metric within this small cohort, not a
universal rating or proof that the player is better. Real-data mode still shows missing-data states
when metrics or suitable peers are absent.

## Similarity search

1. Select players from the reference player's data source only.
2. Exclude records without any tactical metrics. For partial real profiles, fill missing dimensions
with that selected pool's observed mean; generated profiles need no imputation.
3. Standardize each of the five columns with a z-score, so percentages do not overwhelm per-90 rates.
4. Use cosine nearest-neighbor matching: compare the direction of the standardized five-number vectors.
5. Exclude the reference itself; return five nearest alternatives. Scores are
`100 × max(0, cosine_similarity)`, bounded to 0–100 and ordered from highest to lowest.

The comparison pool is the selected dataset, across its leagues and positions; the radar's cohort
is narrower. Similarity reflects statistical shape, not transfer suitability, future performance or
an overall player quality rating. These are transparent algorithms, not a trained outcome predictor.

## Preservation and labeling

API lists accept `dataset=synthetic` or `dataset=real`; omission defaults to real for compatibility.
Each profile response includes `data_source`. Real and synthetic rows are never mixed in similarity
or cohort charts. The main database's original 113 real records were compared before/after seeding:
every stored field remained identical. Exported demo PDFs identify all data as fictional.

Synthetic data makes product exploration possible. It does not replace source collection or turn
the simplified eligibility checker into official FIFA clearance.
