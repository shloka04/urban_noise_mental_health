#!/usr/bin/env python3
"""
Compute the Nocturnal Noise Index from complaint-level 311 data.

The index weights every individual noise complaint by the hour it was filed and
by the severity of its complaint type, then sums those weights per UHF42
neighbourhood. It therefore needs complaint-level records; it cannot be derived
from counts that have already been aggregated.

Input:  data/311_complaint_level.csv
        Columns used (case-insensitive, with or without spaces):
            created_date, complaint_type, latitude, longitude
Output: data/nocturnal_index_by_uhf42.csv
            UHF42, GEONAME, complaint_count, nocturnal_index, period

Complaints are assigned to neighbourhoods by a point-in-polygon join against
data/UHF42.geo.json, which is how the original analysis mapped them.

    python src/build_nocturnal_index.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
COMPLAINTS_CSV = DATA_DIR / "311_complaint_level.csv"
UHF42_GEOJSON = DATA_DIR / "UHF42.geo.json"
OUTPUT_CSV = DATA_DIR / "nocturnal_index_by_uhf42.csv"
REFERENCE_COUNTS = DATA_DIR / "uhf_noise_counts.csv"

# Hour-of-day weights. Overnight complaints count double.
NOCTURNAL_HOURS = range(22, 24), range(0, 7)
PEAK_HOURS = range(7, 10), range(18, 22)

# Severity weights by complaint type, matching the published definition.
COMPLAINT_WEIGHTS = {
    "noise - residential": 1.2,
    "noise - commercial": 1.3,
    "noise - vehicle": 1.1,
    "noise - park": 1.0,
    "noise - house of worship": 1.4,
    "noise - helicopter": 1.8,
    "noise - construction": 1.6,
    "noise - street/sidewalk": 1.1,
    "noise": 1.0,
}


def time_weight(hour: int) -> float:
    if hour >= 22 or hour <= 6:
        return 2.0
    if 7 <= hour <= 9 or 18 <= hour <= 21:
        return 1.5
    return 1.0


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """311 exports vary between 'Created Date' and 'created_date'."""
    renamed = {c: c.strip().lower().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=renamed)
    required = {"created_date", "complaint_type", "latitude", "longitude"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(
            f"Missing required columns: {', '.join(sorted(missing))}\n"
            f"Found: {', '.join(df.columns[:20])}"
        )
    return df


def load_complaints() -> pd.DataFrame:
    if not COMPLAINTS_CSV.exists():
        sys.exit(
            f"{COMPLAINTS_CSV} not found.\n\n"
            "Download the noise complaints from NYC Open Data, for example:\n"
            '  curl -o data/311_complaint_level.csv \\\n'
            '    "https://data.cityofnewyork.us/resource/erm2-nwe9.csv?'
            "$select=created_date,complaint_type,latitude,longitude"
            "&$where=starts_with(complaint_type,'Noise')"
            '&$limit=2000000"'
        )
    df = pd.read_csv(COMPLAINTS_CSV, low_memory=False)
    df = normalise_columns(df)

    # Keep every noise category, not just one. The severity table covers
    # residential, commercial, vehicle, construction, helicopter, worship,
    # park and street/sidewalk.
    df = df[df["complaint_type"].str.strip().str.lower().str.startswith("noise")]
    df = df.dropna(subset=["latitude", "longitude", "created_date"])
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df = df.dropna(subset=["created_date"])
    print(f"Loaded {len(df):,} noise complaints with coordinates and timestamps")
    return df


def assign_neighbourhoods(df: pd.DataFrame) -> pd.DataFrame:
    try:
        import geopandas as gpd
    except ImportError:
        sys.exit("geopandas is required for the spatial join:  pip install geopandas")

    uhf = gpd.read_file(UHF42_GEOJSON)
    points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    )
    if uhf.crs is not None and uhf.crs.to_string() != "EPSG:4326":
        uhf = uhf.to_crs("EPSG:4326")

    joined = gpd.sjoin(points, uhf[["GEOCODE", "GEONAME", "geometry"]],
                       how="inner", predicate="within")
    dropped = len(df) - len(joined)
    print(f"Matched {len(joined):,} complaints to a UHF42 neighbourhood "
          f"({dropped:,} fell outside the boundaries)")
    return joined.rename(columns={"GEOCODE": "UHF42"})


def compute_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["time_weight"] = df["created_date"].dt.hour.map(time_weight)
    df["type_weight"] = (
        df["complaint_type"].str.strip().str.lower().map(COMPLAINT_WEIGHTS).fillna(1.0)
    )
    df["weight"] = df["time_weight"] * df["type_weight"]
    df["period"] = df["created_date"].dt.year

    out = (
        df.groupby(["UHF42", "GEONAME", "period"])
        .agg(complaint_count=("weight", "size"), nocturnal_index=("weight", "sum"))
        .reset_index()
        .sort_values(["period", "UHF42"])
    )
    nocturnal_share = (df["time_weight"] == 2.0).mean()
    print(f"Overnight complaints (22:00-06:59): {nocturnal_share:.1%} of the total")
    return out


def sanity_check(out: pd.DataFrame) -> None:
    """Compare per-neighbourhood counts against the figures already on file."""
    if not REFERENCE_COUNTS.exists():
        return
    ref = pd.read_csv(REFERENCE_COUNTS)
    print("\nPer-year totals against the reference counts in uhf_noise_counts.csv:")
    ref_total = ref["noise_complaint_count"].sum()
    for period, grp in out.groupby("period"):
        total = grp["complaint_count"].sum()
        print(f"  {period}: {total:>8,}   (reference total {ref_total:,})")
    print("Use this to identify which year the published analysis covered.")


def main() -> None:
    complaints = load_complaints()
    located = assign_neighbourhoods(complaints)
    index = compute_index(located)
    index.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV} ({len(index)} neighbourhood-years)")
    sanity_check(index)
    print("\nNow re-run:  python src/noise_analysis.py")


if __name__ == "__main__":
    main()
