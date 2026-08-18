# FTIR - Ground-based ozone total + partial column data

## Data source

FTIR (Fourier Transform InfraRed) ozone data for Sodankyla, hosted on the BIRA-IASB data portal:

https://data.aeronomie.be/dataset/ftir-ozone-o3-groundbased-remote-sensing-at-sodankyla-from-hr125-fts-fmi-instrument

## How to download

Direct download, **no login required**:

```bash
python ground/FTIR/download_ftir.py
```

This fetches the single GEOMS HDF4 file directly into `ground/FTIR/`.
Skips the download if the file already exists.

## File format

- **Format**: GEOMS HDF4 (readable via `netCDF4.Dataset`, no `pyhdf` needed)
- **Coverage**: 2012-03-29 to 2021-09-26 (16,818 measurements)
- **Key variables**:
  - `O3.COLUMN_ABSORPTION.SOLAR` -- total column (units: `Emolec cm^-2`,
    i.e. x10^18 molec/cm^2). Convert to DU: `value * 1e18 / 2.687e16`.
  - `O3.COLUMN.PARTIAL_ABSORPTION.SOLAR` -- partial columns on a 47-level
    altitude grid (units: `Pmolec cm^-2`, i.e. x10^15 molec/cm^2). Convert
    to DU: `value * 1e15 / 2.687e16`. Note the different SI prefix from
    the total column variable (Peta vs Exa) -- do not reuse the same
    conversion factor for both.
  - `ALTITUDE` (km, 47 levels, layer centers) and `ALTITUDE.BOUNDARIES`
    (km, layer edges) -- use these to split the column into tropospheric
    vs stratospheric contributions if needed.
  - `ANGLE.SOLAR_ZENITH.ASTRONOMICAL` -- solar zenith angle per measurement.
