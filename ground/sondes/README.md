# Ozonesonde (ECC) - Vertical ozone profile data

## Data source

Ozonesonde (ECC) data for Sodankyla, available through the public WOUDC API
(`https://api.woudc.org`, no account needed).

## How to download

```bash
python ground/sondes/download_woudc.py
```

Pages through the WOUDC `ozonesonde` collection filtered to Sodankyla
(WOUDC `station_id=262`) and downloads each record's extCSV file from
`https://woudc.org/archive/...` into `sondes_data/woudc/` (gitignored).
As of this writing: 1381 flights, spanning 1988-2026.

API docs: https://api.woudc.org/openapi
Python client alternative: https://github.com/woudc/pywoudc

## WOUDC extCSV file format

Each file has `#TIMESTAMP`, `#FLIGHT_SUMMARY`, and `#PROFILE` sections.

- **`#TIMESTAMP`**: `UTCOffset,Date,Time` -- flight date/time (UTC).
- **`#FLIGHT_SUMMARY`**: includes `IntegratedO3` and `SondeTotalO3`. Use
  `SondeTotalO3` (IntegratedO3 plus the residual above burst altitude,
  normalized to the reference ground instrument) for total column --
  `IntegratedO3` alone excludes that residual and understates the true
  column by roughly 10-15%. Some files use `9999` as a fill value for
  both fields.
- **`#PROFILE`**: per-level `Pressure` and `O3PartialPressure`, but
  their **column position varies by era** (1988-94, 1994-2024, and
  2024-2026 archives all use a different column order) -- always read
  the header row of this section to map column names to positions,
  never assume a fixed index.
- **Data quality**: a handful of files from early 2007 contain corrupted
  values (the literal string `"inf"` as a fill value, a spurious 0 hPa
  pressure reading, or a profile truncated well above the surface) --
  filter with `np.isfinite()` and a plausibility range on the derived
  total column (100-700 DU), since `float("inf")` parses without error.
