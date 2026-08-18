# S5P TROPOMI - Ozone data download (Copernicus)

## Data source

Copernicus Data Space Ecosystem
https://dataspace.copernicus.eu

API: https://catalogue.dataspace.copernicus.eu/odata/v1/Products

## Products

| Product | Description | Size |
|---|---|---|
| `L2__O3____` | Total column ozone | ~340 MB/file (OFFL) |
| `L2__O3__PR_` | Ozone vertical profile | ~120 MB/file (OFFL) — reprocessed `RPRO` granules from the Copernicus catalog run ~390 MB/file |

**Important:**
- The O3 profile product (`L2__O3__PR_`) is only available from **2018-04-30** onward — earlier
  dates return no granules despite TROPOMI having launched in Oct 2017.
- Near Sodankyla, **3-7 granules/day** typically intersect a ±0.5° box (consecutive overlapping
  orbit passes at high latitude). A full-history download of all matching granules is on the
  order of 1+ TB — filter to specific target dates (e.g. sonde flight dates) rather than a
  continuous `DATE_START`/`DATE_END` range spanning years.

## Prerequisites

- A free Copernicus Data Space account: https://dataspace.copernicus.eu/
- Credentials in `.env`: `COPERNICUS_USER`, `COPERNICUS_PASS`
- Dependencies: `requests`, `xarray`, `netCDF4`

## Configuration

Edit the top of `satellite/S5P/S5Pozone.py`:

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
python satellite/S5P/S5Pozone.py
```

## Output

| Directory | Contents |
|---|---|
| `satellite/S5P/s5p_data/total_column/` | Total column NetCDF files (L2__O3____) |
| `satellite/S5P/s5p_data/profile/` | Profile NetCDF files (L2__O3__PR_) |

## File format

- **Format**: NetCDF4
- **Group**: `PRODUCT`
- **Variable**: `ozone_total_vertical_column` (mol/m²)
- **Dimensions**: `(time, scanline, ground_pixel)`
- **Conversion to DU**: multiply by 2241
- **Filtering**: `qa_value > 0.5`, co-located within ±0.5° of station
