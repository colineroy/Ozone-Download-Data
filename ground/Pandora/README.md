# Pandonia - Ozone total column data download

Downloads ozone total column data from the Pandonia Global Network
(https://www.pandonia-global-network.org/). Data is open and public -
no registration, no account, no API key needed. Just run the script.

API: https://api.pandonia-global-network.org/docs#/

## What gets downloaded

`download_pandora.py` queries the PGN API for each date in the
configured range and station, then downloads every matching Level 2
O3 file for that day (in practice there is at most one).

Output file: `ground/Pandora/pandora_data/pandonia_SITE_DATE_L2_CODE.txt`

The file contains all measurements for that day with full column
metadata (52 columns including ozone in mol/m², quality flags,
SZA, etc.). Ozone total column is **column 39** (mol/m²).

Convert to DU: multiply by 2241 (1 DU = 2.69e20 molecules/m², 1 mol = 6.022e23 molecules, so 1 mol/m² = 6.022e23 / 2.69e20 ≈ 2241 DU).

## Configuration

Edit the top of `ground/Pandora/download_pandora.py`:

| Variable | Default | Description |
|---|---|---|
| `SITE` | `"Sodankyla"` | Station name |
| `PAN_ID` | `309` | Pandonia station ID |
| `SPECTROMETER` | `"1"` | Spectrometer number |
| `LEVEL` | `"L2"` | Data level |
| `CODE` | `"rout2"` | Product code (see table below) |
| `DATE_START` | e.g. `"2026-04-04"` | Start date (YYYY-MM-DD) — edit before each run |
| `DATE_END` | e.g. `"2026-09-03"` | End date (YYYY-MM-DD) — edit before each run |
| `BASE` | `"https://api.pandonia-global-network.org/v1"` | API base URL |
| `OUT_DIR` | `ground/Pandora/pandora_data/` (relative to the script itself, so it's safe to run from any working directory) | Output directory |

Note: L2 data for Sodankyla/Pandora309 currently only exists from
**2026-04-04** onward (this instrument's current processing/calibration
version has no earlier data) — requesting earlier dates just returns
"No files found" for every day.

### Common codes

The API only accepts a fixed list of official codes; querying anything
else returns a 400 error naming the valid ones. For this
station/instrument the valid `L2` codes are: `rout2`, `rwvt1`, `rfuh5`,
`rnvh3`, `rnvs3`, `rsus1`, `rfus5` (plus a few `f...`/`smca1` variants).
Only `rout2` (ozone total column) is confirmed/used here.

| Code   | Product               |
|--------|-----------------------|
| rout2  | Ozone total column    |

## How to download

```bash
# From the project root
python ground/Pandora/download_pandora.py
```

No login required — data is public.

Download time is approximately **2 seconds per day**.
