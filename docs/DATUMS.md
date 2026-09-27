# Datums

## Datums in the registry

| Datum | Ellipsoid | Registry entries |
|---|---|---|
| NAD83(2011) | GRS80 | all 222 SPCS zones + EPSG:6318 |
| NAD83(CORS96) | GRS80 | EPSG:6783 |
| WGS 84 (G2296) | WGS84 | all 120 UTM zones + EPSG:4326 |

G2296 is the current operational WGS 84 realization (effective 2024-01-07,
aligned to ITRF2020; it superseded G2139).

## v1 datum-shift policy (explicit)

Transforming between **different** datums in v1 applies a **null
approximation** (identity): the coordinates are carried through unchanged,
and the result records a `DatumPath` with:

- `method = "null-approximation"`
- `accuracy_horizontal_m` — estimated 1-sigma horizontal accuracy
- `region`, `source` (citation), and `warning`

Same-datum transforms use `method = "identity"` with 0.0 m.

| Path | Accuracy (horizontal) | Basis |
|---|---|---|
| NAD83(2011) ↔ NAD83(CORS96) | ~0.05 m (typical ~0.02 m) | 2011 national readjustment moved CORS ~1.8 cm (NC Geodetic Survey) |
| NAD83(2011) ↔ WGS 84 (G2296) | ~2.0 m (CONUS) | frames differ ~1-2 m (Penn State GEOG 862) |
| NAD83(CORS96) ↔ WGS 84 (G2296) | ~2.0 m (CONUS) | composed; dominated by the NAD83/WGS 84 frame difference |

Every `TransformResult` exposes `datum_path` and appends the approximation
warning to `warnings` whenever the path is not exact. **Do not use
inter-datum results for survey control, legal boundaries, or construction
stakeout.** They are suitable for mapping, basemap overlay, and field
navigation.

## Heights

Heights are **ellipsoidal** and pass through every transform unchanged.
There is **no geoid model and no NAVD88 orthometric-height support** in v1 —
that is an explicit non-goal. A future version may add a geoid grid
interpolator and return orthometric heights alongside ellipsoidal ones.

## Why null approximations instead of Helmert parameters?

Published, time-dependent Helmert parameters between these realizations
require epoch handling the v1 API does not yet model (positions move with
plate velocity). Shipping a fake-precise 7-parameter transform without epoch
support would be worse than an honest, well-documented approximation. When
epoch-aware transforms land, they will arrive with per-path accuracy
metadata in the same `DatumPath` structure — the API already carries it.
