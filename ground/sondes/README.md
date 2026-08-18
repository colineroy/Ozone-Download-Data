# Ozonesonde (ECC) - Vertical ozone profile data

## Data source

Ozonesonde data is provided by FMI (Finnish Meteorological Institute)

**Recommended: WOUDC API (auto-download, no login required)**

The homogenized WOUDC extCSV archive for Sodankyla (WOUDC `station_id=262`)
is available through the public WOUDC API (`https://api.woudc.org`, no
account needed):

```bash
python ground/sondes/download_woudc.py
```

This downloads every ozonesonde flight on record for the station (1300+
files as of this writing) directly from `https://woudc.org/archive/...`
into `sondes_data/woudc/`. API docs: https://api.woudc.org/openapi.
Python client alternative: https://github.com/woudc/pywoudc.

TCCON is **not** a relevant source here -- it is a separate ground-based
FTIR network for column CO2/CH4/N2O/CO, not ozonesondes.

**Alternative: raw SHARP files from FMI**

For the raw (non-homogenized) `.q*` files, contact FMI directly -- no
auto-download script exists for these.

## How to get raw SHARP files manually

1. Obtain SHARP-format sonde files (`.q*` extension) from FMI or NDACC
2. Place the files in `ground/sondes/sondes_data/`
3. The main scripts will read them automatically

File naming pattern: `soYYMMDD.qXX` (e.g. `so260415.q08`)

## File format

SHARP ASCII format:

- Multi-line header with metadata
- Trigger line containing `"Sodankyla"` for station identification
- Date from header line 7 (YYYY MM DD)
- Launch hour from the line after `"Sodankyla"`
- Total column ozone (`COL1`) from field index 10 after trigger line
- Units: DU (Dobson Units)

## MATLAB parsers

Additional tools for raw SHARP data are in `ground/sondes/sondes_data/`:

| Script | Purpose |
|---|---|
| `parluku2.m` | Parse raw SHARP binary/ASCII file into arrays |
| `SondeInfo.m` | Extract metadata (launch time, ECC serial, flow rate) |
| `table.m` | Generate sonde inventory spreadsheet |

## Homogenized WOUDC archive (long-term record, 1988-2026)

This is a **separate, much larger archive** from the 2-3 raw SHARP files
above. `download_woudc.py` (see above) fetches it fresh via the WOUDC API
into `sondes_data/woudc/`. Earlier manually-assembled copies of the same
kind of data may also exist locally under `sondes_data/89-94/woudc/`,
`sondes_data/94-24/woudc/`, `sondes_data/24-26/woudc/` -- check for
duplicates before using both.

Format: WOUDC extCSV (HEGIFTOM homogenization), with `#TIMESTAMP`,
`#FLIGHT_SUMMARY`, and `#PROFILE` sections.

- **Total column**: use `SondeTotalO3` (IntegratedO3 plus the residual above
  burst altitude, normalized to the reference ground instrument), **not**
  `IntegratedO3` alone -- the latter excludes that residual and understates
  the true column by roughly 10-15%.
- **Profile**: `Pressure` and `O3PartialPressure` columns, but their
  **position in the `#PROFILE` section varies by era** (1988-94 vs
  1994-2024 vs 2024-2026 all differ) -- always locate columns by name from
  the header row, never by fixed index.
- **Data quality**: a handful of files from early 2007 contain corrupted
  values (the literal string `"inf"` as a fill value, a spurious 0 hPa
  pressure reading, or a profile truncated well above the surface) --
  filter with `np.isfinite()` and a plausibility range on the derived
  total column (100-700 DU), since `float("inf")` parses without error.

## Note on `ground/sondes/MR/`

These files are WOUDC-format but for **Marambio, Antarctica** (station
GAW_ID MBI), not Sodankyla -- leftover from an unrelated station and not
relevant to this repo.
