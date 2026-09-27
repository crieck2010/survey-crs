# Interop

## Consuming engines

- **survey-field v0.2.0** — `--target-crs` on import: accepts an EPSG code or
  a picker query; calls `crs.by_epsg` / `crs.search` to resolve it and
  `crs.transform_coords` to reproject imported points. Datum warnings from
  `TransformResult.warnings` should be surfaced to the operator.
- **survey-suite v0.3.0** — Coordinates toolbox: drives `crs.search`,
  `crs.zones_for_state`, `crs.group_by_type`, and `crs.suggest(lat, lon)`
  for the CRS picker UI.

`survey-crs` never imports its consumers. The optional `survey-geodesy`
backend is lazy: the engine installs and runs standalone, and uses
`geodesy.transverse_mercator` only when the package is importable
(see `crs.backend_name()`).

## API stability

The names in `crs.__all__` are the stable public API for v0.x. `CrsEntry`
gains fields only (never renames) within v0.x; `TransformResult` keeps its
field set. Behavioural changes to projection math are patch-level only when
they fix bugs toward the EPSG definition.

## Data contracts

- `CrsEntry.params`: normalized to **degrees** (angular) and **metres**
  (linear). `CrsEntry.params_epsg` preserves the official EPSG values with
  their published units — use these when citing parameters.
- `CrsEntry.bbox`: `[lon_min, lat_min, lon_max, lat_max]` in degrees, from
  the EPSG area of use. Coarse near borders; `suggest()` may return
  neighbouring zones for borderline points.
- `TransformResult.x/y`: easting/northing in `TransformResult.unit` for
  projected targets; longitude/latitude in degrees (`unit == "deg"`) for
  geographic targets. `h` is always ellipsoidal metres.
- Units: `"m"`, `"ftUS"` (exactly 1200/3937 m), `"ft"` (international,
  exactly 0.3048 m), `"deg"`.

## Scaling notes

- The registry is a checked-in Python literal (345 entries); import cost is
  milliseconds and lookups are dict-based — no I/O, no database.
- Projections are closed-form series (TM/LCC) or a small Newton solve
  (Hotine inverse, ~5 iterations); single-point transforms run in
  microseconds. Batch work should vectorize at the call site (plain loops
  are fine into the hundreds of thousands of points).
- No caching is built in; the functions are pure and thread-safe, so callers
  can memoize or parallelize freely.

## Versioning

Semantic versioning with a Keep-a-Changelog `CHANGELOG.md`. The registry
mirrors the EPSG database as researched 2026-09-27; a future release may
refresh it against a newer EPSG snapshot (registry-data-only change → minor
bump, with the diff noted in the changelog).
