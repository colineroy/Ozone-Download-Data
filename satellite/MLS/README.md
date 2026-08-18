# MLS (Aura) - Ozone profile download (NASA)

## Data source

NASA GES DISC via CMR (Common Metadata Repository)
https://cmr.earthdata.nasa.gov

Data portal: https://disc.gsfc.nasa.gov/

| Product | Collection ID | Description |
|---|---|---|
| ML2O3 | `C1729925806-GES_DISC` | Ozone vertical profile, v5.1 |
| ML2HNO3 | `C1729925263-GES_DISC` | Nitric acid profile, v5.1 (optional, off by default) |

MLS is a limb sounder (microwave, day/night) with a large along-track
footprint (~200 km) -- co-location uses a 500 km radius around Sodankyla
(67.3668N, 26.6297E), much wider than the ~0.5 degree box used for nadir
sounders like OMI.

## Prerequisites

- NASA Earthdata Login account: https://urs.earthdata.nasa.gov/
- Credentials in `.env`: `EARTHDATA_TOKEN` (preferred, avoids Basic Auth
  issues) or `EARTHDATA_USER` + `EARTHDATA_PASS`
- Dependencies: `requests`, `python-dotenv`

## Configuration

Edit the top of `satellite/MLS/MLS_download.py`:

| Variable | Default | Description |
|---|---|---|
| `LAT_SITE` | `67.3668` | Station latitude |
| `LON_SITE` | `26.6297` | Station longitude |
| `DELTA` | `5.0` | Bounding box half-width (degrees, ~500 km) |
| `DATE_START` | `"2026-04-15"` | Start date (YYYY-MM-DD) |
| `DATE_END` | `"2026-04-30"` | End date (YYYY-MM-DD) |
| `DOWNLOAD_HNO3` | `False` | Set `True` to also fetch HNO3 profiles |

## How to download

```bash
# From the project root
python satellite/MLS/MLS_download.py
```

**Note on scope:** MLS/Aura has flown continuously since 2004, so a blind
multi-year download is unnecessarily large (each granule is one full orbit
day, ~2.6 MB). For a sonde-vs-satellite comparison, it is far more efficient
to query CMR per specific target date (e.g. each ECC sonde flight date) than
to set a wide `DATE_START`/`DATE_END` range and download everything in it.

## Output

`satellite/MLS/mls_data/ozone/` -- one `.he5` granule per requested day,
named `MLS-Aura_L2GP-O3_v05-0X-cXX_<year>d<day-of-year>.he5`.

## File format

- **Format**: HDF-EOS5 (`.he5`)
- **Key fields** (under `/HDFEOS/SWATHS/O3/`):
  - `Geolocation Fields/Latitude`, `Longitude`, `Pressure`
  - `Data Fields/O3` (mol/mol), `Status`, `Quality`, `Convergence`
- **Quality filter**: `Status % 2 == 0`, `Quality >= 1.2`, `Convergence <= 1.03`
- **Conversion**: O3 VMR (mol/mol -> ppmv via `*1e6`), then to DU per layer
  via `DU = 0.789 * VMR(ppmv) * dP(hPa)`
- Read by `comparaison/ecc_satellite_profile.py`
