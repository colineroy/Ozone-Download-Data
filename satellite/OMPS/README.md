# OMPS (Suomi-NPP / NOAA-21) - Ozone data download (NASA)

## Data sources

### 1. NASA AVDC (pre-computed overpass files, no auth required)

#### Suomi-NPP NMTO3 (total column)

https://avdc.gsfc.nasa.gov/pub/data/satellite/Suomi_NPP/L2OVP/NMTO3-L2/

| File | Source |
|---|---|
| `suomi_npp_omps_l2ovp_nmto3_v2.1_sodankyla_262.txt` | NMTO3 total column overpass |

#### NOAA-21 LP-L2-O3-DAILY (ozone profile)

https://avdc.gsfc.nasa.gov/pub/data/satellite/NOAA21/OMPS/L2OVP/LP-L2-O3-DAILY_v1.0/

One text file per day, stored under `noaa21_profile/`, ~8 KB each.

The script downloads this file automatically (no auth needed). NOAA-21 launched
November 2022, so no data exists before `2022-11-01`. As of this session the local archive
holds 207 daily files, fetched for all Sodankyla ECC sonde flight dates (+/-1 day) from
2022-11 to 2026-06.

**Performance note:** `ensure_noaa21_avdc()` fetches one day at a time, sequentially, with
no concurrency. Fine for the small `DATE_START`/`DATE_END` default (a couple of days), but
setting it to a multi-year range and running it as-is will be slow (each request that misses
a day still costs a round trip). For a historical backfill, query only the specific dates
you need (e.g. sonde flight dates +/-1 day) with a thread pool, rather than every calendar
day in a wide range.

### 2. NASA GES DISC (full orbit HDF5 via CMR)

https://cmr.earthdata.nasa.gov

| Product | Collection ID | Description |
|---|---|---|
| NMTO3 | `C1386443916-GES_DISC` | Suomi-NPP total column ozone L2 |

## Prerequisites

- For CMR download: NASA Earthdata Login account: https://urs.earthdata.nasa.gov/
- Credentials in `.env`: `EARTHDATA_USER`, `EARTHDATA_PASS` (or `EARTHDATA_TOKEN`)
- Dependencies: `requests`, `h5py`

## Configuration

Edit the top of `satellite/OMPS/download_omps.py`:

| Variable | Default | Description |
|---|---|---|
| `LAT_SITE` | `67.3668` | Station latitude |
| `LON_SITE` | `26.6297` | Station longitude |
| `DELTA` | `0.5` | Co-location window (degrees) |
| `DATE_START` | `"2026-04-15"` | Start date (YYYY-MM-DD) |
| `DATE_END` | `"2026-04-15"` | End date (YYYY-MM-DD) |

## How to download

```bash
# From the project root
python satellite/OMPS/download_omps.py
```

## Output

- `satellite/OMPS/omps_data/` — NMTO3 HDF5 granules (via CMR) + NMTO3 AVDC overpass text file (via HTTP).
- `satellite/OMPS/omps_data/noaa21_profile/` — NOAA-21 LP-L2-O3-DAILY daily profile text files (via AVDC HTTP).

## File format

- **NMTO3**: HDF5 (`.h5`) — total column, units as provided by GES DISC
- **NOAA-21 LP-L2-O3-DAILY**: Text (`.txt`) — daily limb profile, O3 VMR (ppmv) on 60 levels (0.5–60.5 km); convert to DU/layer via `DU = 0.789 * VMR(ppmv) * dP(hPa)`
- NOAA-20 OMPS data is not currently configured (check NOAA STAR or CLASS)
