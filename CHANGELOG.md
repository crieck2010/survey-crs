# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-27

### Added
- 345-entry CRS registry researched from the EPSG registry (per-entry
  epsg.io citation): 222 NAD83(2011) SPCS83 zones (m / ftUS / intl-ft as EPSG
  defines), WGS 84 UTM 1-60 N/S (EPSG:32601-32660, 32701-32760), geographic
  NAD83(2011) (6318), NAD83(CORS96) (6783), WGS 84 (4326).
- Pure-stdlib projection engine: Transverse Mercator, Lambert Conic
  Conformal 2SP, Hotine Oblique Mercator variant A, UTM; forward + inverse
  for every entry. TM uses survey-geodesy lazily when installed, with an
  internal fallback (latitude-of-origin aware in both paths).
- Datum paths with accuracy/source metadata (v1: documented null
  approximations; same-datum paths exact).
- Picker API: `search`, `by_epsg`, `zones_for_state`, `group_by_type`,
  `suggest`.
- CLI: `crs list/search/info/convert`.
- Exact US survey foot (`1200/3937 m`) unit helpers.
- 406 tests: NGS published-coordinate validations to millimetres (NY
  Central/West/Long Island m + ftUS, UTM 18N), PROJ cross-checks, all-345
  round trips, EPSG parameter checks, picker/datum/unit/CLI tests.
- Docs: `docs/SOURCES.md`, `docs/DATUMS.md`, `docs/INTEROP.md`.

### Known limitations
- Inter-datum shifts are null approximations (~2 m NAD83(2011)/WGS 84;
  ~2-5 cm CORS96/2011); not for survey control.
- Ellipsoidal heights only; no geoid/NAVD88.
