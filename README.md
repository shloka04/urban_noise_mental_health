# Urban Noise and Mental Health in New York City

Noise is the single most common complaint New Yorkers make to 311. It is also one of the few environmental exposures a city can actually change through policy. So the question is whether it shows up in mental health at the neighbourhood level — and if it does, whether a smarter measure of noise detects it better than a raw complaint count does.

This project joins every 311 noise complaint to neighbourhood depression prevalence across New York's 42 UHF42 districts, and tests two purpose-built metrics against the naive one.

Published in *Curieux Academic Journal*. The manuscript is in [`paper/`](paper/).

## Two metrics

**Nocturnal Noise Index.** A complaint at 3am is not equivalent to one at 3pm, and a helicopter is not a dog. The index weights every individual complaint by when it was filed and what kind of noise it was:

| Time of day | Weight | | Complaint type | Weight |
|---|---|---|---|---|
| 22:00–06:00 | 2.0 | | Helicopter | 1.8 |
| 07:00–09:00, 18:00–21:00 | 1.5 | | Construction | 1.6 |
| Daytime | 1.0 | | House of worship | 1.4 |
| | | | Commercial | 1.3 |
| | | | Residential | 1.2 |
| | | | Vehicle, street | 1.1 |
| | | | Park | 1.0 |

This matters more than it might sound. Across the current 311 data, **46.9% of noise complaints fall in the 22:00–06:00 window** — against the 37.5% you would get if complaints were spread evenly through the day. Noise complaints really are a nocturnal phenomenon, and neighbourhoods differ in how nocturnal theirs are.

**Population-normalised rate.** Complaints per 100,000 residents, so dense neighbourhoods aren't flagged as noisy purely for being populous. Observed range across the city: 119 to 10,301 per 100,000 — a roughly eighty-fold spread.

## Results

Five regression approaches were compared: simple linear models on raw count and on normalised rate, a multiple-feature model, and a Theil-Sen robust estimator.

```
Raw noise count vs depression       r = 0.167   p = 0.131
Noise rate per 100k vs depression   r = 0.117   p = 0.294
Multiple-features model             R² = 0.057
```

The associations are positive and consistent in direction across every metric, and none reaches significance at α = 0.05 across 42 neighbourhoods.

That is the honest result, and it is the expected one. Depression is multifactorial — income, isolation, healthcare access, housing quality and employment all contribute — so an environmental exposure that explained a large share of neighbourhood variance would be a reason for suspicion rather than celebration. A consistent weak positive signal across independent measures of noise is what a real but modest effect looks like in ecological data.

## Running it

```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy
python3 src/noise_analysis.py
```

To compute the Nocturnal Noise Index you also need complaint-level records, since the index weights each complaint individually and cannot be derived from counts that are already aggregated. The repository ships a builder that fetches them and does the spatial join:

```bash
pip install geopandas
curl -o data/311_complaint_level.csv \
  "https://data.cityofnewyork.us/resource/erm2-nwe9.csv?\$select=created_date,complaint_type,latitude,longitude&\$where=starts_with(complaint_type,'Noise')&\$limit=2000000"
python3 src/build_nocturnal_index.py
python3 src/noise_analysis.py
```

`build_nocturnal_index.py` assigns each complaint to a neighbourhood by point-in-polygon join against the UHF42 boundaries, applies the time and severity weights, and writes a per-neighbourhood index. The analysis script detects it automatically and the nocturnal results come back.

## Repository contents

```
data/    complaint counts, depression prevalence, UHF42 boundaries, ZIP crosswalk
src/     analysis pipeline and the nocturnal index builder
paper/   published manuscript
```

The complaint-level 311 extract runs to millions of rows, so the builder downloads it on demand rather than the repository carrying it.

## Sources

NYC Open Data, 311 Service Requests. NYC Department of Health and Mental Hygiene, Community Health Survey (depression prevalence, MeasureID 1323). Neighbourhood boundaries follow the DOHMH UHF42 definition.

This is an ecological study. Associations between neighbourhood-level noise and neighbourhood-level depression do not transfer to individuals, and nothing here establishes causation.
