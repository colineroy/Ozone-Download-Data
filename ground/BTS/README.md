# BTS - BiTec Sensor Solar Spectroradiometer ozone data

## Data source

BTS data is provided by FMI (Finnish Meteorological Institute).
Contact FMI to obtain the CSV files.

No public API or auto-download script is available.

## File format

CSV with columns:

```
Time (ISO 8691, GMT),Airmass,Ozone (DU),Ozone_STD,Ozone_Uncertainty
```

- Header must contain `"Ozone (DU)"` to be detected
- Timestamp format ends with `Z` (UTC)
- Units: DU (Dobson Units) - no conversion needed

Example filename: `20260410_TOC_BTS_66639_V1.csv`
