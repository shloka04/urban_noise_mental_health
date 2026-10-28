# Urban Noise and Mental Health in New York City

Does living somewhere noisy make people more depressed? New York publishes two things that let you look: every 311 noise complaint since 2010, and neighbourhood-level depression prevalence from the city's Community Health Survey. This project joins them across the 42 UHF42 neighbourhoods.

The short answer is a weak positive association that doesn't reach significance. Noisier neighbourhoods do report somewhat more depression, but noise explains only a small share of the variation, which is what you'd expect for something as multifactorial as depression.

## The data

| File | Contents |
|---|---|
| `data/combined_noise_mental_health_data.csv` | Noise complaint counts joined to depression prevalence, by neighbourhood and survey period |
| `data/uhf_noise_counts.csv` | Complaint counts per UHF42 neighbourhood |
| `data/mental_health_data.json` | Community Health Survey depression estimates (MeasureID 1323) |
| `data/UHF42.geo.json` | Neighbourhood boundaries |
| `data/ZCTA-to-MODZCTA.csv` | ZIP to modified-ZCTA crosswalk used in geocoding |

Depression prevalence comes from the NYC Department of Health and Mental Hygiene Community Health Survey. Complaints come from NYC Open Data's 311 Service Requests.

## Running it

```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy
python src/noise_analysis.py
```

Output goes to `figures/`. Paths resolve relative to the repository, so it runs from any checkout.

## What it computes

Population-normalised noise rates per 100,000 residents, Pearson correlations against depression prevalence, and a set of regression models — simple linear on raw count and on normalised rate, a multiple-feature model, and a Theil-Sen robust estimator.

On the aggregated data in this repository:

```
Raw noise count vs depression       r = 0.167   p = 0.131
Noise rate per 100k vs depression   r = 0.117   p = 0.294
Multiple-features model             R² = 0.057
```

Neither correlation is significant at α = 0.05 with 42 neighbourhoods. Reported as found.

## The Nocturnal Noise Index

`calculate_nocturnal_noise_index()` in `src/noise_analysis.py` implements the index: each complaint is weighted by hour of day (2.0 between 10pm and 6am, 1.5 at peak hours, 1.0 otherwise) and by a severity weight for complaint type (helicopter 1.8, construction 1.6, place of worship 1.4, commercial 1.3, residential 1.2, vehicle and street 1.1, park 1.0).

Computing it needs **complaint-level** records with timestamps and complaint types. The dataset here is already aggregated to neighbourhood-year, so those columns don't exist and the index cannot be derived from it. The pipeline detects this and skips every nocturnal result rather than substituting anything.

To compute it, download the 311 Service Requests extract from NYC Open Data, filter to noise complaints, save it as `data/311_complaint_level.csv`, and re-run. The script picks it up automatically and the nocturnal correlations, models and plots come back.

## What's not here

The raw 311 extract (118,062 noise complaints) is too large to commit and is freely available from NYC Open Data. `TimePeriods.json`, the DOHMH lookup mapping survey period IDs to calendar periods, isn't redistributed either; without it the analysis still runs and the period column keeps its raw IDs.

## Sources

NYC Open Data, 311 Service Requests from 2010 to Present. NYC Department of Health and Mental Hygiene, Community Health Survey.

This is an ecological study at neighbourhood level and cannot establish causation. Associations at the neighbourhood level do not transfer to individuals.
