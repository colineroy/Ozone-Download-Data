"""
brewer_woudc_export.py
=======================
Convert FMI/EUBREWNET Brewer total-column ozone products (Sodankyla,
Brewer #037 primary since 1989-06-22 / #214 secondary since 2013-09-24)
to WOUDC TotalOzone extCSV format.

Source
------
ground/Brewer/brewer_data/SDK_<year>_ozone_product_1_5.txt (EUBREWNET
Level 1.5 product). This is used instead of the NDACC Ames SOTC*.KIR
files (e.g. brewer/SOTC2606.zip in raw_to_woudc) because it carries a
real per-observation std_o3 and airmass -- both mandatory WOUDC #DAILY
fields the KIR files don't provide directly.

Target
------
WOUDC TotalOzone extCSV, one file per (brewer, year-month), following
the block structure of a real WOUDC TotalOzone reference file (Hradec
Kralove, CZE): #CONTENT / #DATA_GENERATION / #PLATFORM / #INSTRUMENT /
#LOCATION / #TIMESTAMP / #DAILY / #TIMESTAMP / #MONTHLY.

Per WOUDC's TotalOzone category spec (guide.woudc.org, Section 3.3.6):
    #DAILY mandatory fields: Date, WLCode, ObsCode, ColumnO3, StdDevO3,
    UTC_Begin, UTC_End, UTC_Mean, nObs, mMu (ColumnSO2 is optional).
    WLCode=9 for all Brewer spectrophotometer measurements.

Known gap -- ObsCode: WOUDC's ObsCode (Direct Sun "0"/DS vs Zenith Sky
"3"/ZS, etc.) records which observation geometry the Brewer used, and
isn't present in the EUBREWNET product columns at all. Hardcoded to "0"
(Direct Sun), the Brewer's standard operating mode at Sodankyla outside
polar night -- a documented approximation, not a measured value. Confirm
with Rigel Kivi / EUBREWNET before a real WOUDC submission if precision
on this field matters.

Author: Coline Roy - Internship FMI Sodankyla, 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Station / instrument metadata
# ---------------------------------------------------------------------------

STATION_ID = "262"          # WOUDC Sodankyla station id (verified this project, NOT the "179" seen in old headers)
STATION_NAME = "Sodankyla"
STATION_COUNTRY = "FIN"
STATION_GAW_ID = "SOD"
STATION_LAT = 67.37
STATION_LON = 26.63
STATION_HEIGHT = 179.0
AGENCY = "FMI"
SCIENTIFIC_AUTHORITY = "Rigel Kivi"

WLCODE_BREWER = 9
OBSCODE_DIRECT_SUN = "0"  # hardcoded approximation -- see module docstring

# Model confirmed from the real NDACC Ames header (SOTC*.KIR, "Brewer #037
# MKII"). #214's model is NOT independently confirmed here -- MKIII is a
# reasonable but unverified placeholder; confirm before a real submission.
BREWER_CFG = {
    37: dict(number="037", model="MKII"),
    214: dict(number="214", model="MKIII"),  # UNCONFIRMED
}


# ---------------------------------------------------------------------------
# Source parsing
# ---------------------------------------------------------------------------

def load_eubrewnet_product(fpath: Path | str) -> pd.DataFrame:
    """Load one SDK_<year>_ozone_product_1_5.txt file into a DataFrame."""
    df = pd.read_csv(fpath, comment="#")
    df["datetime"] = pd.to_datetime(df["gmt"], format="%Y%m%dT%H%M%SZ", utc=True)
    df["date"] = df["datetime"].dt.date
    return df


def load_eubrewnet_years(data_dir: Path | str, years: list[int] | None = None) -> pd.DataFrame:
    """Load and concatenate all (or selected) EUBREWNET L1.5 files.

    Two file conventions coexist in data_dir: station-wide
    "SDK_<year>_..." exports (both Brewers mixed in one file) and
    per-instrument "<brewerid>_<year>_..." exports (single Brewer only,
    sometimes fresher/more complete). Both are merged here, deduplicated
    by (datetime, brewerid) since the same reading can appear in both
    sources -- without dedup, daily_aggregate would silently average
    duplicated observations together.
    """
    data_dir = Path(data_dir)
    patterns = ["SDK_*_ozone_product_1_5.txt",
                "37_*_ozone_product_1_5.txt", "214_*_ozone_product_1_5.txt"]
    files = sorted({f for pattern in patterns for f in data_dir.glob(pattern)})
    if years is not None:
        wanted = {str(y) for y in years}
        files = [f for f in files if f.stem.split("_")[1] in wanted]
    frames = [load_eubrewnet_product(f) for f in files]
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    return df.drop_duplicates(subset=["datetime", "brewerid"]).reset_index(drop=True)


def daily_aggregate(df: pd.DataFrame, brewerid: int) -> pd.DataFrame:
    """
    Aggregate individual EUBREWNET observations into one row per UTC day,
    matching WOUDC's #DAILY semantics.

    StdDevO3 is computed as the standard deviation of that day's ColumnO3
    values across observations (WOUDC's "day-to-day variability" sense),
    not EUBREWNET's own std_o3 (a per-observation instrumental precision
    estimate) -- falling back to std_o3 only when a day has a single
    observation and a true day-level std can't be computed.
    """
    sub = df[df["brewerid"] == brewerid].copy()
    if sub.empty:
        return pd.DataFrame()

    rows = []
    for d, g in sub.groupby("date"):
        g = g.sort_values("datetime")
        n = len(g)
        stddev = float(g["o3"].std(ddof=0)) if n > 1 else float(g["std_o3"].iloc[0])
        rows.append(dict(
            date=d,
            column_o3=float(g["o3"].mean()),
            stddev_o3=stddev,
            utc_begin=g["datetime"].iloc[0],
            utc_end=g["datetime"].iloc[-1],
            utc_mean=g["datetime"].mean(),
            nobs=n,
            mmu=float(g["airmass"].mean()),
        ))
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


# ---------------------------------------------------------------------------
# WOUDC extCSV block construction
# ---------------------------------------------------------------------------

def _fmt(val, fmt=".1f") -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    return format(val, fmt)


def _utc_hours(dt: pd.Timestamp) -> float:
    return dt.hour + dt.minute / 60.0 + dt.second / 3600.0


def _block_content() -> str:
    return "#CONTENT\nClass,Category,Level,Form\nWOUDC,TotalOzone,1.0,1\n"


def _block_data_generation(generation_date: date, version: str = "1.0") -> str:
    return (
        "#DATA_GENERATION\n"
        "Date,Agency,Version,ScientificAuthority\n"
        f"{generation_date.isoformat()},{AGENCY},{version},{SCIENTIFIC_AUTHORITY}\n"
    )


def _block_platform() -> str:
    return (
        "#PLATFORM\n"
        "Type,ID,Name,Country,GAW_ID\n"
        f"STN,{STATION_ID},{STATION_NAME},{STATION_COUNTRY},{STATION_GAW_ID}\n"
    )


def _block_instrument(brewerid: int) -> str:
    cfg = BREWER_CFG[brewerid]
    return (
        "#INSTRUMENT\n"
        "Name,Model,Number\n"
        f"Brewer,{cfg['model']},{cfg['number']}\n"
    )


def _block_location() -> str:
    return (
        "#LOCATION\n"
        "Latitude,Longitude,Height\n"
        f"{STATION_LAT},{STATION_LON},{STATION_HEIGHT}\n"
    )


def _block_timestamp(d: date) -> str:
    return (
        "#TIMESTAMP\n"
        "UTCOffset,Date,Time\n"
        f"+00:00:00,{d.isoformat()}\n"
    )


def _block_daily(daily: pd.DataFrame) -> str:
    lines = [
        "#DAILY",
        "Date,WLCode,ObsCode,ColumnO3,StdDevO3,UTC_Begin,UTC_End,UTC_Mean,NObs,mMu",
    ]
    for _, row in daily.iterrows():
        lines.append(
            f"{row['date'].isoformat()},{WLCODE_BREWER},{OBSCODE_DIRECT_SUN},"
            f"{_fmt(row['column_o3'])},{_fmt(row['stddev_o3'])},"
            f"{_utc_hours(row['utc_begin']):.2f},{_utc_hours(row['utc_end']):.2f},"
            f"{_utc_hours(row['utc_mean']):.2f},{int(row['nobs'])},{_fmt(row['mmu'], '.3f')}"
        )
    return "\n".join(lines) + "\n"


def _block_monthly(daily: pd.DataFrame) -> str:
    month_start = daily["date"].iloc[0].replace(day=1)
    mean_o3 = float(daily["column_o3"].mean())
    std_o3 = float(daily["column_o3"].std(ddof=0)) if len(daily) > 1 else 0.0
    npts = int(daily["nobs"].sum())
    return (
        "#MONTHLY\n"
        "Date,ColumnO3,StdDevO3,Npts\n"
        f"{month_start.isoformat()},{_fmt(mean_o3)},{_fmt(std_o3)},{npts}\n"
    )


# ---------------------------------------------------------------------------
# Main export function
# ---------------------------------------------------------------------------

def write_totalozone_month(
    daily_month: pd.DataFrame,
    brewerid: int,
    output_dir: Path | str = ".",
    version: str = "1.0",
    generation_date: Optional[date] = None,
) -> Path:
    """Write one WOUDC TotalOzone extCSV file covering all days in daily_month
    (should all fall within the same calendar month)."""
    if daily_month.empty:
        raise ValueError("daily_month is empty -- nothing to write.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if generation_date is None:
        generation_date = date.today()

    first_day = daily_month["date"].iloc[0]
    cfg = BREWER_CFG[brewerid]
    fname = f"{first_day.strftime('%Y%m')}.Brewer.{cfg['number']}.{AGENCY}.csv"
    fout = output_dir / fname

    blocks = [
        _block_content(),
        _block_data_generation(generation_date, version),
        _block_platform(),
        _block_instrument(brewerid),
        _block_location(),
        _block_timestamp(daily_month["date"].iloc[0]),
        _block_daily(daily_month),
        _block_timestamp(daily_month["date"].iloc[-1]),
        _block_monthly(daily_month),
    ]
    content = "\n\n".join(b.rstrip("\n") for b in blocks) + "\n"
    fout.write_text(content, encoding="utf-8")
    print(f"WOUDC TotalOzone file written: {fout}")
    return fout


def write_totalozone_batch(
    df: pd.DataFrame,
    brewerid: int,
    output_dir: Path | str = "woudc_totalozone",
    version: str = "1.0",
) -> list[Path]:
    """Aggregate df (raw EUBREWNET observations, any date range) to daily
    values and write one WOUDC file per calendar month present."""
    daily = daily_aggregate(df, brewerid)
    if daily.empty:
        print(f"No data for Brewer #{brewerid}.")
        return []

    daily["year_month"] = daily["date"].apply(lambda d: (d.year, d.month))
    written = []
    for (_, _), month_df in daily.groupby("year_month"):
        try:
            fout = write_totalozone_month(
                month_df.drop(columns="year_month"), brewerid, output_dir=output_dir, version=version,
            )
            written.append(fout)
        except Exception as e:
            import warnings
            warnings.warn(f"Export error for {month_df['date'].iloc[0]}: {e}", UserWarning)
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    data_dir = Path(__file__).parent / "brewer_data"
    output_dir = Path(__file__).parent / "woudc_totalozone"

    years = None
    if len(sys.argv) > 1:
        years = [int(y) for y in sys.argv[1:]]

    print(f"Loading EUBREWNET product files from {data_dir}"
          + (f" (years: {years})" if years else " (all years)"))
    df = load_eubrewnet_years(data_dir, years=years)
    print(f"{len(df)} observation(s) loaded.\n")

    for brewerid in (37, 214):
        print(f"=== Brewer #{brewerid} ===")
        written = write_totalozone_batch(df, brewerid, output_dir=output_dir)
        print(f"{len(written)} WOUDC TotalOzone file(s) written for Brewer #{brewerid}\n")
