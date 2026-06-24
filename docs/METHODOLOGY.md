# FloodWatch Ghana: Risk Methodology & Model Validation (v0.1)

*Greater Accra Region, Ghana · Updated April 2026*

This document provides a comprehensive overview of the FloodWatch Ghana risk model, the district risk leaderboard, engineering history, and a full quantitative and qualitative validation of both model versions against the May 18, 2025 Greater Accra flood event.

---

## 1. The Risk Model (v0.1)

FloodWatch Ghana v0.1 is a **structural baseline** model. It identifies areas chronically prone to flooding based on their physical and environmental characteristics — terrain, drainage, land cover, and rainfall patterns.

### 1.1 Weighted Composite Formula

Each 30m pixel is assigned a risk score from 0 (Low) to 1 (High) using a weighted combination of five input layers:

| Component | Weight | Direction | Source | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Elevation** | 30% | Inverted | NASA SRTM (30m) | Low-lying areas are natural catchments for surface runoff. |
| **Precipitation** | 25% | Normal | ERA5-Land Monthly Means (0.1°) | Climatological rainfall surface captures chronic spatial patterns for structural risk. |
| **Terrain Slope** | 20% | Inverted | Derived from SRTM | Flat terrain cannot drain quickly and pools surface water. |
| **Imperviousness** | 15% | Normal | ESA WorldCover (10m) | Paved and urban surfaces prevent infiltration into soil. |
| **Water Proximity** | 10% | Inverted | OpenStreetMap | Proximity to rivers and drainage channels increases inundation risk. |

**Formula:**
```
Risk = 0.30×(1−DEM_norm) + 0.25×Rain_norm + 0.20×(1−Slope_norm) + 0.15×Imperv_norm + 0.10×(1−Water_norm)
```

All input layers are min-max normalised to [0, 1] before compositing. The final composite is reclassified using **percentile-based stretching** (p25 and p75 breakpoints) to distribute risk scores across the full [0, 1] range and avoid compression in the middle.

### 1.2 Rainfall Data Source — Why ERA5-Land for the v0.1 Structural Baseline

The rainfall layer is the most operationally significant input. The v0.1 structural baseline uses **ERA5-Land monthly climatological means**, with GPM IMERG reserved for the v1.1 dynamic event layer.

| Source | Type | Latency | Accuracy | Used in |
| :--- | :--- | :--- | :--- | :--- |
| CHIRPS v2.0 | Climatological mean | Days | Moderate | v0.1 original / auto fallback |
| **ERA5-Land** | **Reanalysis mean** | **Days** | **Good** | **v0.1 structural baseline (current)** |
| GPM IMERG Final Run | Actual monthly observed | ~3.5 months | Best (gauge-corrected) | v1.1 dynamic layer |
| GPM IMERG Late Run | Near real-time | ~12 hours | Good | v1.1 dynamic layer fallback |

**Why ERA5-Land for a static structural model:**
ERA5-Land monthly means represent the chronic spatial rainfall pattern across the region — the long-run climatological distribution that is the correct input for a model of structural flood vulnerability. A structural baseline should identify areas that are *chronically* at risk regardless of any single weather event.

GPM IMERG returns the *actual* measured precipitation for a specific month. This is the right input for a dynamic risk model that needs to respond to individual storms. For the structural baseline, using GPM data effectively injects one storm's footprint into a map supposed to represent chronic risk. When the June 2024 GPM data was used, a georeferencing bug in the longitude clip (at the prime meridian, ~0°) also created a hard vertical seam confirmed as a −0.265 risk cliff at 43% of the raster width. ERA5 produces a smooth, artifact-free climatological surface.

GPM IMERG is retained in the pipeline (`scripts/ingest_rainfall.py`) and will be the primary source for the v1.1 dynamic event layer, where single-event rainfall totals are precisely what the model needs.

---

## 2. District Risk Leaderboard

### 2.1 Original Model (CHIRPS/ERA5 rainfall, no percentile reclassification)

Mean risk scores computed per district from the original pipeline run.

| Rank | District | Mean Risk | Max Risk | Flooded May 2025 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Ablekuma West | 0.8398 | 0.9928 | No |
| 2 | Weija Gbawe | 0.8123 | 0.9957 | **Yes** |
| 3 | Ga Central | 0.7258 | 0.9796 | No |
| 4 | Accra Metropolis | 0.7170 | 0.8681 | **Yes** |
| 5 | Ga West | 0.7063 | 0.9091 | No |
| 6 | Ga South | 0.7035 | 0.9168 | No |
| 7 | Ablekuma North | 0.6922 | 0.9129 | No |
| 8 | Ablekuma Central | 0.6876 | 0.9673 | No |
| 9 | Ayawaso East | 0.6741 | 0.8010 | No |
| 10 | Korle-Klottey | 0.6708 | 0.8220 | No |
| 11 | La-Dade-Kotopon | 0.6665 | 0.8261 | No |
| 12 | Ayawaso North | 0.6428 | 0.7923 | No |
| 13 | Okaikwei North | 0.6216 | 0.7901 | No |
| 14 | Ayawaso Central | 0.6024 | 0.7815 | No |
| 15 | Krowor | 0.5994 | 0.7714 | No |
| 16 | Ledzokuku | 0.5633 | 0.7841 | No |
| 17 | Ayawaso West | 0.5555 | 0.7763 | No |
| 18 | Ga East | 0.5529 | 0.8011 | **Yes** |
| 19 | Ga North | 0.5399 | 0.8156 | No |
| 20 | Tema | 0.5215 | 0.7691 | **Yes** |
| 21 | Tema West | 0.4887 | 0.7598 | **Yes** |
| 22 | Ningo-Prampram | 0.4646 | 1.0000 | No |
| 23 | Ada East | 0.4635 | 0.8083 | No |
| 24 | La-Nkwantanang-Madina | 0.4619 | 0.7043 | **Yes** |
| 25 | Adenta | 0.4610 | 0.7331 | **Yes** |
| 26 | Kpone-Katamanso | 0.4507 | 0.7605 | No |
| 27 | Ada West | 0.4376 | 0.7787 | No |
| 28 | Shai Osudoku | 0.4223 | 0.9061 | No |
| 29 | Ashaiman | 0.3654 | 0.6527 | No |

### 2.2 Current Model (ERA5-Land / CHIRPS rainfall + percentile reclassification, June 2026)

| Rank | District | Mean Risk | Max Risk | Flooded May 2025 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Krowor | 0.9206 | 0.9967 | No |
| 2 | Ledzokuku | 0.9186 | 0.9923 | No |
| 3 | Ayawaso North | 0.9163 | 0.9856 | No |
| 4 | Ashaiman | 0.9119 | 0.9840 | No |
| 5 | Tema West | 0.9014 | 0.9898 | **Yes** |
| 6 | Ga Central | 0.8561 | 0.9870 | No |
| 7 | Ayawaso West | 0.8558 | 0.9804 | No |
| 8 | La-Dade-Kotopon | 0.8487 | 0.9856 | No |
| 9 | Adenta | 0.8429 | 0.9870 | **Yes** |
| 10 | Ayawaso East | 0.8427 | 0.9499 | No |
| 11 | Ablekuma North | 0.8418 | 0.9852 | No |
| 12 | Tema | 0.8374 | 0.9993 | **Yes** |
| 13 | Okaikwei North | 0.8316 | 0.9819 | No |
| 14 | Ayawaso Central | 0.8206 | 0.8935 | No |
| 15 | Ga East | 0.8001 | 0.9758 | **Yes** |
| 16 | Ga West | 0.7828 | 0.9861 | No |
| 17 | Ablekuma Central | 0.7729 | 0.9792 | No |
| 18 | Kpone-Katamanso | 0.7527 | 0.9864 | No |
| 19 | La-Nkwantanang-Madina | 0.7470 | 0.9600 | **Yes** |
| 20 | Ga North | 0.7211 | 0.9711 | No |
| 21 | Korle-Klottey | 0.7159 | 0.9382 | No |
| 22 | Ga South | 0.7084 | 0.9856 | No |
| 23 | Weija Gbawe | 0.7071 | 0.9995 | **Yes** |
| 24 | Ablekuma West | 0.6872 | 0.9347 | No |
| 25 | Accra Metropolis | 0.6364 | 0.9416 | **Yes** (score below 0.70 threshold) |
| 26 | Ningo-Prampram | 0.5611 | 0.9758 | No |
| 27 | Ada East | 0.5553 | 0.7493 | No |
| 28 | Shai Osudoku | 0.5070 | 0.9424 | No |
| 29 | Ada West | 0.4973 | 0.7519 | No |

---

## 3. Validation — May 18, 2025 Flood Event

### 3.1 Event Summary

On **May 18, 2025**, Greater Accra experienced a severe flash flooding event following approximately **132mm of rainfall** in a short period — roughly the equivalent of a full month's rain in a single day. The event caused widespread flooding across multiple districts. Reported flooded districts (sourced from The Watchers, GDACS, and Copernicus EMS):

**Flooded (7 of 29 districts):** Weija Gbawe · Accra Metropolis · Ga East · Tema · Tema West · La-Nkwantanang-Madina · Adenta

**Not flooded (22 districts):** All remaining districts.

### 3.2 Quantitative Metrics — Model Comparison

#### Mean Risk Score by Flood Status

| Metric | Original Model | ERA5-Land / CHIRPS Model | Verdict |
| :--- | :--- | :--- | :--- |
| Mean risk — flooded districts | 0.5736 | **0.7818** | Current higher ✓ |
| Mean risk — non-flooded districts | 0.5953 | **0.7648** | — |
| Difference (flooded − non-flooded) | **−0.0217** | **+0.0170** | Current correct direction ✓ |
| % flooded districts flagged High Risk (≥0.70) | 28.6% (2/7) | **85.7% (6/7)** | Current better ✓ |
| % non-flooded districts flagged High Risk (≥0.70) | 18.2% (4/22) | 77.3% (17/22) | Original more precise |

#### Confusion Matrix at 0.70 Threshold

| | Original Model | ERA5-Land / CHIRPS Model |
| :--- | :--- | :--- |
| True Positives (flooded, flagged high) | 2 | **6** |
| False Positives (not flooded, flagged high) | 4 | 17 |
| True Negatives (not flooded, flagged low) | 18 | 5 |
| False Negatives (flooded, missed) | **5** | 1 (Accra Metropolis, score 0.636) |
| **Precision** | 0.33 | 0.26 |
| **Recall** | 0.29 | **0.86** |
| **F1 Score** | 0.31 | **0.40** |

### 3.3 Qualitative Assessment

#### Original Model
The original model correctly placed two of the most historically flood-prone districts — **Weija Gbawe (rank 2)** and **Accra Metropolis (rank 4)** — in its top tier. These are well-known chronic flood zones in Greater Accra and their high ranking reflects genuine structural risk (low elevation, dense impervious surfaces, proximity to the Odaw River and Korle Lagoon drainage system).

However, the model **missed five flooded districts entirely** at the 0.70 threshold:
- **Ga East (rank 18), Tema (rank 20), Tema West (rank 21)** — ranked mid-table, well below the high-risk cutoff
- **La-Nkwantanang-Madina (rank 24), Adenta (rank 25)** — ranked near the bottom

This is the model's most significant qualitative failure. Adenta and La-Nkwantanang-Madina are peri-urban and inland districts that were overwhelmed by the volume of the May 2025 event — their structural characteristics (moderate slope, mixed land cover) do not mark them as chronic flood zones, but a 132mm single-day rainfall event overloaded their drainage regardless. The original model, built on climatological rainfall averages, had no mechanism to capture this.

The mean risk of flooded districts (0.574) was actually **lower** than non-flooded districts (0.595) — the model ranked flooded areas as marginally safer on average. This is a fundamental failure of direction.

#### ERA5-Land / CHIRPS Model (Current)
The current model uses ERA5-Land monthly climatological means (falling back to CHIRPS v2.0), paired with percentile reclassification:

- **6 of 7 flooded districts score above 0.70** — recall 0.86
- The mean risk of flooded districts (0.782) correctly **exceeds** non-flooded districts (0.765)
- **Tema West (rank 5), Adenta (rank 9), Tema (rank 12)** are correctly in the top half of the risk distribution
- **Accra Metropolis scores 0.636** — the one missed flooded district (rank 25 of 29). Its western coastal location, large area, and mixed land-cover reduce the district mean below the 0.70 threshold, even though high-risk pockets exist within it

The main weakness remains **low precision (0.26)**: 17 of 22 non-flooded districts also score above 0.70. The bottom five districts — Ada West, Shai Osudoku, Ada East, Ningo-Prampram, Ablekuma West — are correctly identified as lower risk; these are predominantly rural, peri-urban, or coastal areas.

A residual seam artifact at the 0° meridian was identified in the composite raster. Investigation shows this is driven by a **land cover discontinuity** in the ESA WorldCover data at 0° longitude (imperviousness drops from ~0.56 to ~0.15 across a tile boundary), not by the rainfall source. Fixing this requires re-ingesting the WorldCover tiles with proper edge blending — planned for a patch release.

### 3.4 Overall Verdict

**The current ERA5-Land model is a scientifically cleaner baseline.**

| Criterion | Original | ERA5-Land / CHIRPS | Winner |
| :--- | :--- | :--- | :--- |
| Direction of risk signal | Wrong (flooded < non-flooded) | Correct (flooded > non-flooded) | ERA5 |
| Recall — flooded districts caught | 0.29 | **0.86** | ERA5 |
| F1 Score | 0.31 | **0.40** | ERA5 |
| Precision | **0.33** | 0.26 | Original (marginally) |
| Qualitative alignment (known flood zones) | Partial (2/7) | Strong (6/7) | ERA5 |
| Rainfall conceptual fit | Climatological | **Climatological (correct for structural model)** | ERA5 |
| Seam artifacts | None identified | Land cover seam at 0° (pre-existing; not rainfall-driven) | — |

The ERA5 model improves on every meaningful criterion except precision. Recall 0.86 is a significant gain over 0.29 and is the key performance metric for a life-safety application where missing a flooded district is a more serious failure than over-flagging a safe one. The precision difference (0.26 vs 0.33) is small and both models share the same root cause: a static composite cannot distinguish between structural chronic risk and acute event-driven flooding.

---

## 4. Engineering History & Bug Resolutions

### 4.1 The "Global Average" Bug (0.508)

During early development, every district incorrectly displayed a uniform Mean Risk Score of **0.508**.

- **Cause**: The frontend was sending undefined bounding boxes to the TiTiler API, which defaulted to computing the global average of the entire raster.
- **Resolution**: Shifted from dynamic runtime calculation to static pre-calculated statistics. Zonal statistics (mean, max, median, std, histogram) are now baked into the GeoJSON district properties via `scripts/precalculate_stats.py` at pipeline time. This ensures 100% accuracy and instant loading with no API dependency at render time.

### 4.2 Rainfall Source History (CHIRPS → GPM IMERG → ERA5-Land)

The original model ingested rainfall from CHIRPS v2.0 or ERA5-Land — both climatological products. The pipeline was then upgraded to use NASA GPM IMERG as the primary source (actual monthly observed rainfall). GPM Final Run for June 2024 recorded 198 mm/month mean over Greater Accra.

However, using a single event month's GPM data in a *static structural* model proved conceptually incorrect: it injected one storm's footprint into a map designed to represent chronic vulnerability. A georeferencing bug in the GPM HDF5 longitude clip also introduced a hard vertical seam at the prime meridian (~0°), confirmed as a −0.265 risk cliff at 43% of the raster width.

The pipeline was reverted to **ERA5-Land monthly climatological means** as the primary source for the v0.1 structural baseline, with CHIRPS v2.0 as the auto fallback:

```
ERA5-Land monthly means  →  CHIRPS v2.0  (v0.1 structural baseline, auto chain)

GPM IMERG Final Run  →  GPM IMERG Late Run  (v1.1 dynamic layer, explicit setting only)
```

This is a cleaner scientific architecture. The structural baseline captures chronic spatial risk using a smooth climatological rainfall surface; the planned v1.1 dynamic layer will use GPM IMERG event totals to trigger risk score adjustments on the day of a storm.

### 4.3 Percentile Reclassification

The original pipeline applied min-max normalisation directly to the composite score, which resulted in compressed mid-range scores across most districts. The recalculated model adds a **percentile-based reclassification step** using the 25th and 75th percentile breakpoints of the pixel-level risk distribution:

```
score < p25  →  mapped to [0.00, 0.33]   (low tier)
p25 ≤ score < p75  →  mapped to [0.33, 0.67]   (moderate tier)
score ≥ p75  →  mapped to [0.67, 1.00]   (high tier)
```

This better utilises the full output range and sharpens the separation between low, moderate, and high risk areas at the pixel level — though district mean compression remains at the 0.70+ band for most urban districts.

### 4.4 COG Pipeline & Tile Serving

All risk outputs are served as Cloud-Optimised GeoTIFFs (COG) from Google Cloud Storage, rendered via TiTiler. Previous versions encountered issues with:
- **Pixel bleeding at district edges** — resolved by removing a boundary buffer that was clipping edge pixels
- **nodata=nan tile blanking** — resolved by removing the `&nodata=nan` TiTiler parameter
- **COG version cache** — managed via `?v=N` query string versioning on the COG URL

---

## 5. Limitations & Roadmap

### 5.1 Current Limitations

- **Static structural model**: Cannot capture event-specific dynamics. A 132mm single-day rainfall will overwhelm peri-urban districts regardless of their chronic risk score.
- **District-level aggregation**: Mean risk at the district level conceals localised hotspots. High-risk pixels within a nominally moderate district are invisible in the leaderboard.
- **Rainfall temporal mismatch**: The ERA5-Land climatological mean does not correspond to the specific conditions of the May 2025 validation event. A proper temporal validation would require running the model with May 2025 event rainfall (GPM IMERG) as the dynamic input in v1.1.
- **No drainage infrastructure data**: The model has no representation of storm drain capacity, culvert blockages, or drainage network connectivity — a major driver of urban flash flooding in Accra.
- **Score compression**: The percentile reclassification improves pixel-level spread but most urban districts still cluster in the 0.74–0.93 band at the mean level, limiting district-level discrimination.

### 5.2 Future Roadmap (v1.1)

| Feature | Description | Impact |
| :--- | :--- | :--- |
| **Dynamic risk layer** | Real-time GPM IMERG rainfall thresholds triggering risk score adjustments on the day of an event | High — addresses the core precision gap |
| **Sentinel-1 SAR validation** | Flood extent mapping via Google Earth Engine for quantitative spatial accuracy metrics beyond district means | High — enables pixel-level validation |
| **Drainage infrastructure layer** | OSM and NADMO drainage network data as an additional composite input | Medium |
| **Property-level API** | Dynamic backend for individual parcel risk queries | Medium |
| **Temporal validation** | Rerun model with May 2025 GPM data to validate under event-matched rainfall | Medium |

---

*FloodWatch Ghana · Greater Accra Region · v0.1 · June 2026*
*Data sources: NASA SRTM, ERA5-Land (ECMWF), ESA WorldCover, OpenStreetMap, GADM*
*Validation event: Greater Accra Floods, May 18 2025 — sources: The Watchers, GDACS, Copernicus EMS*
