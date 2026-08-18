# Ozone Data Download - Sodankylä, Finland

Scripts to download total column and vertical profile ozone data for the
Sodankylä FMI station (67.37°N, 26.63°E), from ground-based instruments and satellite archives.

This repository is **download tooling only** - it does not contain any
comparison, plotting, or analysis code.

## Supported Instruments

| Instrument | Type | Period | Source | Auto-download | Units |
|---|---|---|---|---|---|
| SAOZ | Ground | 2012-2026 | `http://saoz.obs.uvsq.fr/saoz/O3_YYYY.SK` | Direct download (no login) | DU |
| Pandora | Ground | 2026-04 - 2026-06 | PGN REST API (`api.pandonia-global-network.org`) | API (no login) | mol/m^2 -> x2241 -> DU |
| Brewer #037 | Ground | 1989-06 - 2026 (EUBREWNET); 2026-03 - 2026-04 (FMI CSV) | EUBREWNET API (restricted access) / FMI portal | Partial: script exists, but the API needs special EUBREWNET authorisation; falls back to manual FMI download otherwise | DU |
| Brewer #214 | Ground | 2013-09 - 2026 (EUBREWNET, low volume); 2026-03 - 2026-04 (FMI CSV) | EUBREWNET API (restricted access) / FMI portal | Same as #037 | DU |
| BTS | Ground | 2026-04-10 - 2026-04-16 | Local files | No | DU |
| FTIR | Ground | 2012-2021 | BIRA-IASB data portal (`data.aeronomie.be`) | Direct download (no login) | Emolec cm^-2 -> x37.214 -> DU |
| Ozonesonde (ECC) | Ground | 1988-2026 (WOUDC, 1381 records) | WOUDC API (`api.woudc.org`) | Direct download (no login) | DU |
| S5P TROPOMI total column | Satellite | 2026-04 | Copernicus Data Space OData API | API (credentials required) | mol/m^2 -> x2241 -> DU |
| S5P TROPOMI profile | Satellite | 2018-04 - 2026 (sampled) | Copernicus Data Space OData API | API (credentials required) | mol/m^2 -> x2241 -> DU |
| GOME-2A (MetOp-A) | Satellite | 2007-2021 (AVDC), decommissioned | NASA AVDC | Direct HTTP (no login) | DU |
| GOME-2B (MetOp-B) | Satellite | 2013-2019 (AVDC), 2026-04 - 2026-08 (NRT) | `eumdac` (EUMETSAT) / NASA AVDC | NRT: API (credentials req.) / Archive: direct HTTP | DU |
| GOME-2C (MetOp-C) | Satellite | 2019-2026 (AVDC), 2026-04 - 2026-08 (NRT) | `eumdac` (EUMETSAT) / NASA AVDC | NRT: API (credentials req.) / Archive: direct HTTP | DU |
| OMI (Aura) | Satellite | 2004-2026 (total col); 2004-10 - 2021-02 (profile) | NASA GES DISC via CMR / NASA AVDC | API (credentials required) | DU (x0.01) |
| OMPS NMTO3 (Suomi-NPP) | Satellite | 2012-2026 | NASA GES DISC via CMR / NASA AVDC | API (credentials required) | DU |
| OMPS NOAA-21 profile | Satellite | 2022-11 - 2026-06 | NASA AVDC | Direct HTTP (no login) | DU/layer |
| MLS (Aura) | Satellite | 2004-10 - 2026 (sampled to sonde flights) | NASA GES DISC via CMR | API (credentials required) | 0.789 x VMR(ppmv) x dP -> DU/layer |

## Quick Start

1. **Install Git** from https://git-scm.com/ (if not already installed)
2. Clone the repository:
   ```bash
   git clone https://github.com/colineroy/Ozone-Download-and-Comparison-Data.git
   cd Ozone-Download-and-Comparison-Data
   ```
3. **Install Python dependencies** (recommended: use a virtual environment):
   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   # source venv/bin/activate   # Mac/Linux
   pip install -r requirements.txt
   ```
4. Set up credentials in `.env` (see below), then run the downloader for the
   instrument you need (see [Standalone Downloaders](#standalone-downloaders)).

## Credentials

Create a `.env` file at the project root with the variables you need.
Register on each service to obtain your credentials:

| Service | Used by | Where to register | `.env` variables |
|---|---|---|---|
| Copernicus Data Space | S5P TROPOMI | https://dataspace.copernicus.eu/ | `COPERNICUS_USER`, `COPERNICUS_PASS` |
| EUMETSAT Data Store | GOME-2 | https://data.eumetsat.int/ -> profile -> API Keys | `EUMETSAT_KEY`, `EUMETSAT_SECRET` |
| NASA Earthdata | OMI, OMPS, MLS | https://urs.earthdata.nasa.gov/ | `EARTHDATA_USER`, `EARTHDATA_PASS` (or `EARTHDATA_TOKEN`) |
| EUBREWNET | Brewer (API, restricted) | https://eubrewnet.aemet.es/eubrewnet/default/registration | `EUBREWNET_USER`, `EUBREWNET_PASS` (optional) |

Example `.env` file:

```
COPERNICUS_USER=your_email@example.com
COPERNICUS_PASS=your_password
EUMETSAT_KEY=your_consumer_key
EUMETSAT_SECRET=your_consumer_secret
EARTHDATA_USER=your_username
EARTHDATA_PASS=your_password
EARTHDATA_TOKEN=
# EUBREWNET_USER=your_username    # optional (API restricted)
# EUBREWNET_PASS=your_password
```

## Standalone Downloaders

Each instrument with auto-download has a dedicated script. Edit the
configuration variables (`DATE_START`, `DATE_END`, etc.) at the top of the
script, then run it directly.

| Instrument | Script | Command | Config Variables |
|---|---|---|---|
| SAOZ | `ground/SAOZ/download_saoz.py` | `python ground/SAOZ/download_saoz.py` | `STATION`, `YEAR` |
| Pandora | `ground/Pandora/download_pandora.py` | `python ground/Pandora/download_pandora.py` | `PAN_ID`, `DATE_START`, `DATE_END` |
| Brewer (EUBREWNET API) | `ground/Brewer/download_brewer.py` | `python ground/Brewer/download_brewer.py` | `DATE_START`, `DATE_END`, `BREWER_IDS` |
| FTIR | `ground/FTIR/download_ftir.py` | `python ground/FTIR/download_ftir.py` | none (single fixed file) |
| Ozonesonde (ECC, WOUDC archive) | `ground/sondes/download_woudc.py` | `python ground/sondes/download_woudc.py` | `STATION_ID` |
| S5P TROPOMI | `satellite/S5P/S5Pozone.py` | `python satellite/S5P/S5Pozone.py` | `DATE_START`, `DATE_END`, `PRODUCTS_TO_DOWNLOAD` |
| GOME-2 (NRT + Archive) | `satellite/GOME2/gome2_download.py` | `python satellite/GOME2/gome2_download.py` | `DATE_START`, `DATE_END` |
| OMI | `satellite/OMI/download_omi.py` | `python satellite/OMI/download_omi.py` | `DATE_START`, `DATE_END` |
| OMPS (total column + NOAA-21 profile) | `satellite/OMPS/download_omps.py` | `python satellite/OMPS/download_omps.py` | `DATE_START`, `DATE_END` |
| MLS | `satellite/MLS/MLS_download.py` | `python satellite/MLS/MLS_download.py` | `DATE_START`, `DATE_END`, `DOWNLOAD_HNO3` |

BTS and the raw-SHARP (non-homogenized) ozonesonde files have no download
script and must be placed manually - see the instrument's `README.md`.

**Performance note:** several of these scripts query the source day-by-day
with no concurrency (GOME-2's AVDC archive, OMPS's NOAA-21 AVDC archive).
This is fine for a short date range, but setting `DATE_START`/`DATE_END` to
span years and running as-is will be slow. For a historical backfill,
query only the specific dates you actually need (in parallel with a thread
pool) rather than every calendar day in a wide range.

## Dependencies

```bash
pip install -r requirements.txt
```

```
requests>=2.31
python-dotenv>=1.0
eumdac>=2.2
```

`eumdac` is only needed for the GOME-2 NRT downloader.
