# GOME-2 - Ozone data download

Two complementary data sources for total column O3 at Sodankyla:

| Source | Period | Format | Auth |
|---|---|---|---|
| NRT (EUMETSAT Data Store) | Last ~60 days | HDF5 (`.HDF5`) | EUMETSAT API key |
| Archive (NASA AVDC) | 2007-present | Text files (`.txt`) | None (HTTP) |

## Source 1: NRT (EUMETSAT Data Store)

Collection: `EO:EUM:DAT:METOP:NTO` — Near Real-Time Total Column O3

**Note:** despite the collection name, the downloaded HDF5 files (`S-O3M_GOME_O3-NO2-...`) are
multi-product files that also contain the **vertical ozone profile**
(`/DETAILED_RESULTS/O3/O3Profile` + `/DETAILED_RESULTS/O3/O3ProfilePressure`). There is no
separate GOME-2 profile collection on the EUMETSAT Data Store, and no offline/historical
archive for the profile product — only the rolling ~60-day NRT window gives profile data.
The AVDC archive below (source 2) is total column only.

### Prerequisites
- Free account: https://data.eumetsat.int/
- API keys: https://api.eumetsat.int/api-key/
- `.env`: `EUMETSAT_KEY`, `EUMETSAT_SECRET`
- `pip install eumdac`

### Configuration

Edit the top of `satellite/GOME2/gome2_download.py`:

| Variable | Default | Description |
|---|---|---|
| `LAT` | `67.37` | Station latitude |
| `LON` | `26.63` | Station longitude |
| `DELTA` | `0.5` | Bounding box half-width (degrees) |
| `DATE_START` | edit before each run | Start date (YYYY-MM-DD) — capped by the ~60-day NRT retention, so keep it recent |
| `DATE_END` | edit before each run | End date (YYYY-MM-DD), typically today |
| `COLLECTION_ID` | `"EO:EUM:DAT:METOP:NTO"` | EUMETSAT collection |

### Output

`satellite/GOME2/GOME2_data/` — HDF5 files with original filenames.
Ozone in DU (no conversion needed).

---

## Source 2: Archive (NASA AVDC)

Pre-computed overpass text files collocated at Sodankyla (67.367N, 26.630E).

### URL

```
https://avdc.gsfc.nasa.gov/pub/data/satellite/MetOp/GOME2/V03/L2OVP/
```

### Files

| Satellite | File | Period |
|---|---|---|
| MetOp-A (GOME-2A) | `GOME2A/gome2a_l2ovp_sodankyla.txt` | 2007-01-23 — 2021-11-09 (decommissioned) |
| MetOp-B (GOME-2B) | `GOME2B/gome2b_l2ovp_sodankyla.txt` | 2013-01-02 — 2019-02-03 |
| MetOp-C (GOME-2C) | `GOME2C/gome2c_l2ovp_sodankyla.txt` | 2019-01-20 — present |

### Columns (space-separated)

| Column | Description | Units |
|---|---|---|
| `Datetime` | ISO timestamp `YYYYMMDDTHHMMSSmmmZ` | - |
| `DOY` | Day of year | - |
| `Day` | Days since 1950-01-01 | - |
| `Orbit` | Orbit number | - |
| `Scan` | Pixel index within scan | - |
| `Lat.` | Pixel center latitude | deg |
| `Lon.` | Pixel center longitude | deg |
| `Dist.` | Distance from station | km |
| `SZA` | Solar zenith angle | deg |
| `Cld.Fr.` | OCRA cloud fraction | - |
| `Cld.Pr.` | OCRA cloud pressure | mbar |
| `VCD_O3` | Total column O3 | **DU** |
| `VCD_BrO` / `VCD_H2O` / ... | Other trace gases | various |

Fill values: `-1.0000e+00` for O3, other gases similar.

### Download (auto)

`gome2_download.py` downloads all 3 files automatically into `satellite/GOME2/GOME2_avdc/`.
No credentials needed.

---

## How to run

```bash
# From project root - downloads both NRT HDF5 + AVDC archive
python satellite/GOME2/gome2_download.py
```

### Notes

**Why are AVDC points noisier than NRT HDF5 points?**

The NRT HDF5 product is quality-filtered (`qa_col == 0`) and uses a small spatial box
(+-0.5 deg, ~22 x 55 km), so only the best-quality pixels are included. The AVDC archive
includes **all** valid pixels within a **100 km** radius -- up to 15-20 pixels per overpass
(the 24 GOME-2 swath pixels over 2-3 scan lines) with no quality filter (clouds, swath
edges, high SZA all pass through), so it has more scatter.
