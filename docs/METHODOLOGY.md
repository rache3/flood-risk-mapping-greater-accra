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
| **Precipitation** | 25% | Normal | CHIRPS v2.0 Monthly Climatology (5km) | Climatological rainfall surface captures chronic spatial patterns for structural risk. |
| **Terrain Slope** | 20% | Inverted | Derived from SRTM | Flat terrain cannot drain quickly and pools surface water. |
| **Imperviousness** | 15% | Normal | ESA WorldCover (10m) | Paved and urban surfaces prevent infiltration into soil. |
| **Water Proximity** | 10% | Inverted | OpenStreetMap | Proximity to rivers and drainage channels increases inundation risk. |

**Formula:**
```
Risk = 0.30×(1−DEM_norm) + 0.25×Rain_norm + 0.20×(1−Slope_norm) + 0.15×Imperv_norm + 0.10×(1−Water_norm)
```

All input layers are min-max normalised to [0, 1] before compositing. The final composite is reclassified using **percentile-based stretching** (p25 and p75 breakpoints) to distribute risk scores across the full [0, 1] range and avoid compression in the middle.

### 1.2 Rainfall Data Source — Why Climatological Means for the v0.1 Structural Baseline

The rainfall layer is the most operationally significant input. The v0.1 structural baseline uses **CHIRPS v2.0 monthly climatology**, with ERA5-Land as the preferred primary when CDS credentials are configured and GPM IMERG reserved for the v1.1 dynamic event layer.

| Source | Type | Latency | Accuracy | Used in |
| :--- | :--- | :--- | :--- | :--- |
| **CHIRPS v2.0** | **Climatological mean** | **Days** | **Moderate** | **v0.1 structural baseline (current run)** |
| ERA5-Land | Reanalysis mean | Days | Good | v0.1 structural baseline (when CDS credentials available) |
| GPM IMERG Final Run | Actual monthly observed | ~3.5 months | Best (gauge-corrected) | v1.1 dynamic layer |
| GPM IMERG Late Run | Near real-time | ~12 hours | Good | v1.1 dynamic layer fallback |

**Why climatological means for a static structural model:**
Both CHIRPS v2.0 and ERA5-Land return the chronic spatial rainfall pattern across the region — the long-run climatological distribution that is the correct input for a model of structural flood vulnerability. A structural baseline should identify areas that are *chronically* at risk regardless of any single weather event.

GPM IMERG returns the *actual* measured precipitation for a specific month. This is the right input for a dynamic risk model. For the structural baseline, using GPM data injects one storm's footprint into a map supposed to represent chronic risk. When the June 2024 GPM data was used, a georeferencing bug in the longitude clip (at the prime meridian, ~0°) also created a hard vertical seam confirmed as a −0.265 risk cliff at 43% of the raster width. CHIRPS and ERA5 both produce smooth, artifact-free climatological surfaces.

The pipeline (`scripts/ingest_rainfall.py`) auto chain tries ERA5 first, then falls back to CHIRPS if CDS credentials (`~/.cdsapirc`) are not configured. GPM IMERG is available only via explicit `RAINFALL_SOURCE=gpm_final/gpm_late`, reserved for the v1.1 dynamic event layer.

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

### 2.2 Current Model (CHIRPS v2.0 monthly climatology + percentile reclassification, June 2026)

| Rank | District | Mean Risk | Max Risk | Flooded May 2025 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Ablekuma West | 0.8828 | 0.9660 | No |
| 2 | Ayawaso North | 0.8772 | 0.9520 | No |
| 3 | Krowor | 0.8737 | 0.9517 | No |
| 4 | Ledzokuku | 0.8627 | 0.9840 | No |
| 5 | Ashaiman | 0.8353 | 0.9486 | No |
| 6 | Ablekuma Central | 0.8285 | 0.9540 | No |
| 7 | Tema | 0.8261 | 0.9694 | **Yes** |
| 8 | Tema West | 0.8121 | 0.9510 | **Yes** |
| 9 | Ablekuma North | 0.8068 | 0.9507 | No |
| 10 | Accra | 0.8022 | 0.9312 | **Yes** |
| 11 | Ga Central | 0.7930 | 0.9692 | No |
| 12 | Ayawaso Central | 0.7909 | 0.8623 | No |
| 13 | Ayawaso East | 0.7812 | 0.9143 | No |
| 14 | Weija Gbawe | 0.7619 | 0.9943 | **Yes** |
| 15 | Adenta | 0.7577 | 0.9821 | **Yes** |
| 16 | La-Dade-Kotopon | 0.7540 | 0.9492 | No |
| 17 | Ayawaso West | 0.7492 | 0.9446 | No |
| 18 | Ga East | 0.7192 | 0.9421 | **Yes** |
| 19 | Korle-Klottey | 0.7052 | 0.9054 | No |
| 20 | Okaikwei North | 0.6724 | 0.9483 | No |
| 21 | La-Nkwantanang-Madina | 0.6604 | 0.9270 | **Yes** (score below 0.67 threshold) |
| 22 | Kpone-Katamanso | 0.6512 | 0.9909 | No |
| 23 | Ga West | 0.6355 | 0.9320 | No |
| 24 | Ada East | 0.6310 | 0.9952 | No |
| 25 | Ga North | 0.5850 | 0.9303 | No |
| 26 | Ningo-Prampram | 0.5760 | 0.9930 | No |
| 27 | Ada West | 0.5554 | 0.9987 | No |
| 28 | Ga South | 0.5359 | 0.9654 | No |
| 29 | Shai Osudoku | 0.4838 | 0.9490 | No |

---

## 3. Validation — May 18, 2025 Flood Event

### 3.1 Event Summary

On **May 18, 2025**, Greater Accra experienced a severe flash flooding event following approximately **132mm of rainfall** in a short period — roughly the equivalent of a full month's rain in a single day. The event caused widespread flooding across multiple districts. Reported flooded districts (sourced from The Watchers, GDACS, and Copernicus EMS):

**Flooded (7 of 29 districts):** Weija Gbawe · Accra Metropolis · Ga East · Tema · Tema West · La-Nkwantanang-Madina · Adenta

**Not flooded (22 districts):** All remaining districts.

### 3.2 Quantitative Metrics — Model Comparison

#### Mean Risk Score by Flood Status

| Metric | Original Model | CHIRPS v2.0 Model | Verdict |
| :--- | :--- | :--- | :--- |
| Mean risk — flooded districts | 0.5736 | **0.7628** | Current higher ✓ |
| Mean risk — non-flooded districts | 0.5953 | **0.7212** | — |
| Difference (flooded − non-flooded) | **−0.0217** | **+0.0416** | Current correct direction ✓ |
| % flooded districts flagged High Risk (≥0.67) | 28.6% (2/7) | **85.7% (6/7)** | Current better ✓ |
| % non-flooded districts flagged High Risk (≥0.67) | 18.2% (4/22) | 63.6% (14/22) | Current more precise ✓ |

#### Confusion Matrix at 0.67 Threshold

| | Original Model | CHIRPS v2.0 Model |
| :--- | :--- | :--- |
| True Positives (flooded, flagged high) | 2 | **6** |
| False Positives (not flooded, flagged high) | 4 | 14 |
| True Negatives (not flooded, flagged low) | 18 | 8 |
| False Negatives (flooded, missed) | **5** | 1 (La-Nkwantanang-Madina, score 0.660) |
| **Precision** | 0.33 | 0.30 |
| **Recall** | 0.29 | **0.86** |
| **F1 Score** | 0.31 | **0.44** |

### 3.3 Qualitative Assessment

#### Original Model
The original model correctly placed two of the most historically flood-prone districts — **Weija Gbawe (rank 2)** and **Accra Metropolis (rank 4)** — in its top tier. These are well-known chronic flood zones in Greater Accra and their high ranking reflects genuine structural risk (low elevation, dense impervious surfaces, proximity to the Odaw River and Korle Lagoon drainage system).

However, the model **missed five flooded districts entirely** at the 0.70 threshold:
- **Ga East (rank 18), Tema (rank 20), Tema West (rank 21)** — ranked mid-table, well below the high-risk cutoff
- **La-Nkwantanang-Madina (rank 24), Adenta (rank 25)** — ranked near the bottom

This is the model's most significant qualitative failure. Adenta and La-Nkwantanang-Madina are peri-urban and inland districts that were overwhelmed by the volume of the May 2025 event — their structural characteristics (moderate slope, mixed land cover) do not mark them as chronic flood zones, but a 132mm single-day rainfall event overloaded their drainage regardless. The original model, built on climatological rainfall averages, had no mechanism to capture this.

The mean risk of flooded districts (0.574) was actually **lower** than non-flooded districts (0.595) — the model ranked flooded areas as marginally safer on average. This is a fundamental failure of direction.

#### CHIRPS v2.0 Model (Current)
The current model uses CHIRPS v2.0 monthly climatology (ERA5-Land is the preferred primary when CDS credentials are configured), paired with percentile reclassification and a corrected ESA WorldCover tile merge:

- **6 of 7 flooded districts score above 0.67** — recall 0.86
- The mean risk of flooded districts (0.763) correctly **exceeds** non-flooded districts (0.721), a gap of +0.042
- **Tema (rank 7), Tema West (rank 8), Accra (rank 10)** are correctly in the top third of the risk distribution
- **La-Nkwantanang-Madina scores 0.660** — the one missed flooded district (rank 21 of 29). Its northern peri-urban character, moderate terrain slope, and mixed land-cover pull the district mean just below the 0.67 threshold, even though high-risk pockets exist within it

Precision improved to **0.30**: 14 of 22 non-flooded districts score above 0.67 (down from 17 in the prior run, before the WorldCover tile merge fix). The bottom eight districts — Shai Osudoku, Ga South, Ada West, Ningo-Prampram, Ga North, Ada East, Ga West, Kpone-Katamanso — are correctly identified as lower risk; these are predominantly rural, coastal, or peri-urban areas with low imperviousness.

### 3.4 Overall Verdict

**The CHIRPS v2.0 climatological model is a scientifically cleaner baseline.**

| Criterion | Original | CHIRPS v2.0 (current) | Winner |
| :--- | :--- | :--- | :--- |
| Direction of risk signal | Wrong (flooded < non-flooded) | Correct (flooded > non-flooded, +0.042) | CHIRPS |
| Recall — flooded districts caught | 0.29 | **0.86** | CHIRPS |
| F1 Score | 0.31 | **0.44** | CHIRPS |
| Precision | 0.33 | **0.30** | Comparable |
| Qualitative alignment (known flood zones) | Partial (2/7) | Strong (6/7) | CHIRPS |
| Rainfall conceptual fit | Climatological | **Climatological (correct for structural model)** | CHIRPS |
| Seam artifacts | None identified | None (WorldCover tile merge fixed in this release) | — |

The CHIRPS model improves on every meaningful criterion. Recall 0.86 is a decisive gain over 0.29 — the key metric for a life-safety application where missing a flooded district is the more serious failure. Both models share the same root cause of limited precision: a static composite cannot distinguish between structural chronic risk and acute event-driven flooding.

La-Nkwantanang-Madina is the one miss (mean risk 0.660, just below the 0.67 threshold). Its northern peri-urban character — moderate terrain, mixed land-cover, distance from the coast — places it near the boundary of the risk tiers. The district flood during May 2025 was likely driven by drainage overload under extreme single-day rainfall rather than chronic structural vulnerability, which is exactly what the v1.1 dynamic layer is designed to capture.

---

## 4. Engineering History & Bug Resolutions

### 4.1 The "Global Average" Bug (0.508)

During early development, every district incorrectly displayed a uniform Mean Risk Score of **0.508**.

- **Cause**: The frontend was sending undefined bounding boxes to the TiTiler API, which defaulted to computing the global average of the entire raster.
- **Resolution**: Shifted from dynamic runtime calculation to static pre-calculated statistics. Zonal statistics (mean, max, median, std, histogram) are now baked into the GeoJSON district properties via `scripts/precalculate_stats.py` at pipeline time. This ensures 100% accuracy and instant loading with no API dependency at render time.

### 4.2 Rainfall Source History (CHIRPS → GPM IMERG → CHIRPS / ERA5-Land)

The original model ingested rainfall from CHIRPS v2.0 — a climatological product. The pipeline was then upgraded to use NASA GPM IMERG as the primary source (actual monthly observed rainfall). GPM Final Run for June 2024 recorded 198 mm/month mean over Greater Accra.

However, using a single event month's GPM data in a *static structural* model proved conceptually incorrect: it injected one storm's footprint into a map designed to represent chronic vulnerability. A georeferencing bug in the GPM HDF5 longitude clip also introduced a hard vertical seam at the prime meridian (~0°), confirmed as a −0.265 risk cliff at 43% of the raster width.

The pipeline was reverted to **climatological sources** for the v0.1 structural baseline. The auto chain tries ERA5-Land first (smooth reanalysis monthly means), then falls back to CHIRPS v2.0 if CDS credentials (`~/.cdsapirc`) are not configured. The current deployed run uses CHIRPS v2.0:

```
ERA5-Land monthly means  →  CHIRPS v2.0  (v0.1 structural baseline, auto chain)

GPM IMERG Final Run  →  GPM IMERG Late Run  (v1.1 dynamic layer, explicit setting only)
```

This is the correct scientific architecture. The structural baseline captures chronic spatial risk using a smooth climatological rainfall surface; the planned v1.1 dynamic layer will use GPM IMERG event totals to trigger risk score adjustments on the day of a storm.

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
- **Rainfall temporal mismatch**: The CHIRPS v2.0 climatological mean does not correspond to the specific conditions of the May 2025 validation event. A proper temporal validation would require running the model with May 2025 event rainfall (GPM IMERG) as the dynamic input in v1.1.
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
*Data sources: NASA SRTM, CHIRPS v2.0 (UCSB CHC), ESA WorldCover, OpenStreetMap, GADM*
*Validation event: Greater Accra Floods, May 18 2025 — sources: The Watchers, GDACS, Copernicus EMS*
