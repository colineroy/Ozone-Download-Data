# Instruments

| Instrument | Type | Period | File Format | Auto Download | Unit Conversion | Status |
|---|---|---|---|---|---|---|
| SAOZ | Ground | 2012–2026 | Text | Yes (HTTP) | Direct (DU) | Active |
| Pandora | Ground | 2026-04 – 2026-06 | Text | Yes (PGN API) | ×2241 (mol/m²→DU) | Active |
| Brewer #037 | Ground | 2026-03 – 2026-04 (FMI CSV); 1989-06 – 2026 (EUBREWNET) | FMI CSV (manual) / EUBREWNET L1.5 | No (FMI portal / manual EUBREWNET zip) | Direct (DU) | Active |
| Brewer #214 | Ground | 2026-03 – 2026-04 (FMI CSV); 2013-09 – 2026 (EUBREWNET, low volume) | FMI CSV (manual) / EUBREWNET L1.5 | No (FMI portal / manual EUBREWNET zip) | Direct (DU) | Active |
| BTS | Ground | 2026-04-10 – 2026-04-16 | CSV | No (local file) | Direct (DU) | Active |
| FTIR | Ground | 2012–2021 | HDF4 (GEOMS) | No (NDACC/BIRA) | Emolec cm⁻² ×37.214→DU | Active |
| Ozonesonde (ECC) | Ground | 2026-03 – 2026-04 (3 raw SHARP profiles); 1988–2026 (1962 WOUDC homogenized) | SHARP ASCII / WOUDC extCSV | No (local file) | Layer integration to COL1 / SondeTotalO3 | Active |
| S5P TROPOMI total col | Satellite | 2026-04 | NetCDF4 | Yes (Copernicus) | ×2241 (mol/m²→DU) | Active |
| S5P TROPOMI profile | Satellite | 2018-04 – 2026 (sampled) | NetCDF4 | Yes (Copernicus) | ×2241 (mol/m²→DU) | Active |
| GOME-2A (MetOp-A) | Satellite | 2007–2021 (AVDC text) | Text (AVDC) | No (decommissioned) | Direct (DU) | Inactive |
| GOME-2B (MetOp-B) | Satellite | 2013–2019 (AVDC), 2026-04 – 2026-08 (NRT HDF5) | HDF5 + Text | Yes (EUMDAC + AVDC) | Direct (DU) | Active |
| GOME-2C (MetOp-C) | Satellite | 2019–2026 (AVDC), 2026-04 – 2026-08 (NRT HDF5) | HDF5 + Text | Yes (EUMDAC + AVDC) | Direct (DU) | Active |
| OMI (Aura) | Satellite | 2004–2026 (total col); 2004-10 – 2021-02 (profile) | HE5 + Text | Yes (AVDC) | ×0.01→DU | Active |
| OMPS NMTO3 (Suomi-NPP) | Satellite | 2012–2026 | HDF5 + Text | Yes (CMR + AVDC) | Direct (DU) | Active |
| OMPS NOAA-21 profile | Satellite | 2022-11 – 2026-06 (207 files) | Text | Yes (AVDC) | 0.789×VMR×ΔP→DU/layer | Active |
| MLS (Aura) profile | Satellite | 2004-10 – 2026 (sampled to sonde flights) | HDF-EOS5 (he5) | Yes (NASA Earthdata) | 0.789×VMR(ppmv)×ΔP→DU/layer | Active |
