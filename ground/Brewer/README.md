# Brewer - Ozone data for Sodankylä

## Data source

Brewer total column ozone data for Sodankylä (Brewers #037, #214) is
downloaded manually from the **Finnish Meteorological Institute (FMI)** open
data portal. There is no automated download script - CSV files must be placed
in `brewer_data/` by hand.

### FMI observation portal (recommended)

URL: https://hav.fmi.fi/hav/asema/?fmisid=101932&page=obs

Steps:
1. Open the link above (Sodankylä Tähtelä, FMISID=101932)
2. Set the date range with the **Alkaen** (start) and **Päättyen** (end) fields
3. Scroll to the bottom of the observations table
4. Click **Hae** to download the CSV file
5. Place the downloaded file in `Brewer/brewer_data/`

The CSV filename follows the pattern `st-lpnn-7501fmisid-101932-csv-*.csv`.

`comparaison/gs_comparison.py` detects these files automatically as long as the filename
contains `fmisid`.

### Column names expected by the reader

| Column in CSV | Description |
|---|---|
| `OZONE #37 (DU)` | Brewer #037 total column ozone (Dobson Units) |
| `OZONE #214 (DU)` | Brewer #214 total column ozone (Dobson Units) |

Additional columns for date/time: `OBSDATE_UTC` (DD.MM.YYYY), `OBSTIME_UTC` (HH:MM).

### Long-term record: EUBREWNET L1.5 archive files (SDK_YYYY_ozone_product_1_5.txt)

This is the **primary source for the long-term record** (1989-2026,
~166,000 measurements for #037 alone) -- distinct from the FMI CSV files
above, which only cover short recent campaign windows.

1. Download the yearly `SDK_YYYY_ozone_product_1_5.txt.zip` archive files
   from the EUBREWNET portal (one per year) into your `Downloads` folder.
2. Unzip each into `Brewer/brewer_data/SDK_YYYY_ozone_product_1_5.txt`
   (a small local script that automates this step, `extract_brewernet.py`,
   is kept out of git but can be recreated trivially -- it just unzips
   `SDK_*_ozone_product_1_5.txt.zip` from `~/Downloads` into `brewer_data/`).

Each file contains **both** Brewer #037 and #214 measurements, distinguished
by the `brewerid` column (37 or 214) -- #037 has been the continuous primary
instrument since 1989-06-22; #214 appears from 2013-09-24 onward as a
secondary/backup unit at much lower volume (a few percent of #037's yearly
count). Any reader of this archive must filter on `brewerid` explicitly --
it is easy to silently mix the two instruments' data otherwise.

Key columns (comma-separated, header at line 52): `brewerid`, `gmt` (ISO
timestamp), `o3` (total column, DU), `filter_flag` (keep only rows where
this is `0`).

### EUBREWNET API (restricted access)

The European Brewer Network (EUBREWNET) provides a REST API documented at:
https://eubrewnet.aemet.es/dokuwiki/doku.php?id=codes:dbaccess

However, API access requires **special authorisation** from the EUBREWNET
administrators - simply having a web account on the portal is not sufficient.
The API enforces role-based access control that a standard user account does
not satisfy.

If you have been granted API access, configure your credentials in `.env`:
```
EUBREWNET_USER=your_username
EUBREWNET_PASS=your_password
```

## File format

The FMI CSVs are semicolon-delimited with the following structure:

```
FMISID;LPNN;OBSDATE_UTC;OBSTIME_UTC;...;OZONE #37 (DU);OZONE #214 (DU);...
101932;7501;15.04.2026;10:30;...;364.2;358.9;...
```

- Units: Dobson Units (DU) - no conversion needed.
- Brewer measurements are sparse (daylight hours only), most rows have empty
  OZONE columns.

## Directory layout

```
Brewer/
+-- README.md                       # This file
+-- brewer_data/                    # Place FMI CSVs here
|   +-- st-lpnn-7501fmisid-101932-csv-*.csv
+-- Brewer_Technical_Documentation.docx
```
