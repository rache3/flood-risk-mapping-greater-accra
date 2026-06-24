# FloodWatch Ghana — Flood Risk Intelligence Application
### Greater Accra Region

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.19748220.svg)](https://doi.org/10.5281/zenodo.19748220)

**Author:** Rachel Atia · GeoBuilders Africa  
**Version:** v0.1 (Baseline Risk)
**Live map:** https://floodwatch.geobuildersafrica.com  
**Company:** https://geobuildersafrica.com  
**GitHub:** https://github.com/rache3/floodwatch-ghana

---

## Overview

An automated flood risk mapping pipeline for Greater Accra, Ghana. The system ingests five geospatial datasets, normalises and combines them into a weighted composite risk score, and serves the output as a live interactive web map updated monthly.

Greater Accra is the pilot region. The pipeline is designed to scale across all regions of Ghana and other African cities.

---

## Live map

> **https://floodwatch.geobuildersafrica.com**

- Flood risk raster rendered with plasma colormap (0 = low risk, 1 = high risk)
- All 29 districts of Greater Accra with boundary overlays
- Click any district for mean, max, median, std deviation, and risk distribution
- Layer toggles and opacity control
- Validation badge — validated against May 18, 2025 Greater Accra floods

---

## Validation

FloodWatch Ghana v0.1 was validated against the **May 18, 2025 Greater Accra flood event** — 132mm of rainfall, 4 deaths, 3,000+ displaced. Flooded districts were sourced from The Watchers, GDACS, and Copernicus EMS.

**Result: Recall 0.86 · F1 0.40 · 6 of 7 flooded districts correctly flagged as high risk**

| Metric | Value |
|---|---|
| Flooded districts mean risk | 0.782 |
| Non-flooded districts mean risk | 0.765 |
| Flooded districts flagged high risk (≥0.70) | 6 of 7 (86%) |
| Recall | 0.86 |
| Precision | 0.26 |
| F1 Score | 0.40 |

Six of 7 flooded districts — Tema West, Adenta, Tema, Ga East, La-Nkwantanang-Madina, Weija Gbawe — scored above 0.70. Accra Metropolis scored 0.636, narrowly below the high-risk threshold. The low precision (17 of 22 non-flooded districts also score high) reflects a known limitation of static structural models applied to a region where most urban districts share similar coastal, low-lying terrain. Improving precision requires dynamic, event-driven inputs — planned for v1.1.

Full Methodology & District Leaderboard: [floodwatch.geobuildersafrica.com/METHODOLOGY.html](https://floodwatch.geobuildersafrica.com/METHODOLOGY.html)

---

## Risk model

```
Risk = 0.30 × (1 − norm_DEM)
     + 0.25 × norm_Rainfall
     + 0.20 × (1 − norm_Slope)
     + 0.15 × norm_Landcover
     + 0.10 × (1 − norm_Waterbodies)
```

| Layer | Weight | Direction | Source | Rationale |
|---|---|---|---|---|
| Elevation (SRTM DEM) | 30% | Inverted | OpenTopography | Low-lying areas accumulate water |
| Precipitation | 25% | Normal | CHIRPS v2.0 Monthly Climatology | Chronic rainfall pattern drives runoff |
| Terrain slope | 20% | Inverted | Derived from SRTM | Flat terrain drains poorly |
| Land cover imperviousness | 15% | Normal | ESA WorldCover 2021 | Impervious surfaces increase runoff |
| Distance to water bodies | 10% | Inverted | OpenStreetMap | Proximity to rivers increases risk |

Each layer is min-max normalised to [0, 1]. The composite score uses percentile-based reclassification at p25/p75, producing three risk tiers: low (0–0.33), moderate (0.33–0.67), and high (0.67–1.0).

---

## Pipeline architecture

```
Input data sources
(OpenTopography · ERA5-Land/CHIRPS · ESA S3 · OpenStreetMap Overpass API)
              │
              ▼
    scripts/ingest.py
    ├── ingest_dem.py          ← SRTM 30m DEM via OpenTopography API
    ├── ingest_slope.py        ← Slope derived from DEM using NumPy gradient
    ├── ingest_rainfall.py     ← ERA5-Land → CHIRPS (v0.1); GPM IMERG retained for v1.1
    ├── ingest_landcover.py    ← ESA WorldCover 2021 → imperviousness fraction
    ├── ingest_waterbodies.py  ← OSM water features → distance raster
    └── ingest_aod.py          ← MODIS/MERRA-2 AOD → quality flagging (optional)
              │
              ▼
    scripts/flood_risk.py
    ├── Align all layers to DEM reference grid
    ├── Min-max normalisation per layer
    ├── Weighted composite risk score
    ├── Percentile-based reclassification
    ├── Mask to Greater Accra boundary
    └── Write Cloud-Optimised GeoTIFF (COG)
              │
              ▼
    scripts/upload_gcs.py      ← Upload COG and GeoJSON to GCS
              │
              ▼
    Google Cloud Storage       ← flood_risk_map.cog.tif + district GeoJSON
              │
              ▼
    TiTiler on Cloud Run       ← Serves COG as XYZ tiles
              │
              ▼
    docs/index.html            ← MapLibre GL JS web map (GitHub Pages)
```

Orchestrated by **GitHub Actions** on a monthly cron schedule. Authentication uses **Workload Identity Federation** — no API keys stored in the repository.

---

## Repository structure

```
floodwatch-ghana/
├── .github/
│   └── workflows/
│       ├── ci.yml             # Lint, structure validation, syntax checks
│       └── pipeline.yml       # Monthly pipeline — build, process, upload
├── scripts/
│   ├── ingest.py              # Orchestrator
│   ├── ingest_dem.py          # SRTM DEM download
│   ├── ingest_slope.py        # Slope derivation
│   ├── ingest_rainfall.py     # ERA5-Land / CHIRPS precipitation (GPM IMERG for v1.1)
│   ├── ingest_landcover.py    # ESA WorldCover
│   ├── ingest_waterbodies.py  # OSM water features
│   ├── ingest_aod.py          # AOD quality flagging
│   ├── flood_risk.py          # Risk model
│   ├── upload_gcs.py          # GCS upload
│   └── validate_flood_risk.py # Validation against historical flood events
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── docs/
│   ├── index.html         # MapLibre GL JS web map
│   ├── METHODOLOGY.html   # Risk model methodology & validation (rendered)
│   └── METHODOLOGY.md     # Risk model methodology & validation (source)
├── output/
│   └── validation_may2025.json # Validation results
├── data/
│   └── gadm41_GHA_accra.json  # District boundaries
├── .env.example               # Configuration template
├── requirements.txt
└── README.md
```

---

## Quickstart — run locally

```bash
git clone https://github.com/rache3/floodwatch-ghana.git
cd floodwatch-ghana

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your credentials

python scripts/ingest.py        # Download all input data
python scripts/flood_risk.py    # Process and write COG
python scripts/upload_gcs.py    # Upload to GCS

# Optional: run validation
python scripts/validate_flood_risk.py
```

---

## Data sources

| Dataset | Source | Resolution | Auth |
|---|---|---|---|
| Elevation (DEM) | SRTM GL1 via OpenTopography | 30m | Free API key |
| Precipitation | CHIRPS v2.0 / ERA5-Land (ECMWF CDS) | 5km / 0.1° | Free / CDS account |
| Slope | Derived from SRTM | 30m | — |
| Land cover | ESA WorldCover 2021 | 10m | Free |
| Water bodies | OpenStreetMap Overpass API | Variable | Open |
| Geocoding | Photon (Komoot / OSM) | — | Open |
| District boundaries | GADM v4.1 | — | Free |

---

## Infrastructure

| Service | Role |
|---|---|
| Google Cloud Run | TiTiler tile server |
| Google Cloud Storage | COG raster and GeoJSON |
| GitHub Actions | CI and monthly pipeline |
| GitHub Pages | Web map hosting |
| Terraform | Infrastructure as code |
| Workload Identity Federation | Keyless GCP authentication |

---

## Known limitations

- **No pixel-level validation** — validation is at the district mean level against reported flood locations. Quantitative spatial validation using Sentinel-1 SAR flood extent maps is planned for v1.1
- Static risk model captures chronic structural vulnerability — not event-driven flash flooding
- Districts like Adenta and La-Nkwantanang-Madina may flood under extreme rainfall events not predicted by the static model
- Real-time rainfall thresholds via GPM IMERG Late Run are planned for v1.1 dynamic layer
- Greater Accra pilot only — expansion to other Ghana regions in progress

---

## Citation

If you use this software or data in your research, please cite it as:

> Atia, R. (2026). *FloodWatch Ghana: Flood Risk Intelligence for Greater Accra* (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.19748220

Or use the `CITATION.cff` file in this repository — GitHub will surface a **Cite this repository** button automatically.

---

*Greater Accra Region, Ghana · EPSG:4326 · Rachel Atia · GeoBuilders Africa · 2025–2026*
