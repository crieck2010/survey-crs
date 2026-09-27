# survey-crs

**CRS registry and coordinate transforms** — engine #12 of the SurveySuite
land-surveying toolbox. Pure Python, standard library only; `survey-geodesy`
is an optional, lazily-imported backend for Transverse Mercator.

## What it is

- **345-entry CRS registry**, every entry researched from the EPSG registry
  (per-entry citation URL included):
  - all 222 NAD83(2011) SPCS83 zones — metres, US survey feet, and
    international-foot variants exactly as EPSG defines them
  - WGS 84 / UTM zones 1–60, north and south (EPSG:32601–32660, 32701–32760)
  - geographic: NAD83(2011) (EPSG:6318), NAD83(CORS96) (EPSG:6783),
    WGS 84 (EPSG:4326)
- **Projection engine**: Transverse Mercator, Lambert Conic Conformal 2SP,
  Hotine Oblique Mercator variant A (Alaska zone 1), and UTM — forward and
  inverse for every entry, verified to millimetres against NGS-published
  coordinates and against PROJ as the EPSG reference implementation.
- **Datum handling with honest accuracy metadata**: every inter-datum path
  carries method, region, estimated accuracy, source, and an explicit
  warning. v1 uses null (identity) approximations between distinct datums —
  fine for mapping, never for survey control.
- **Picker API** for the Coordinates toolbox: `search`, `by_epsg`,
  `zones_for_state`, `group_by_type`, `suggest`.
- **CLI**: `crs list/search/info/convert`.
- NY first-class: Long Island, Central, and West in metres **and** US survey
  feet (plus NY East, which is an official zone).

Heights are **ellipsoidal only** — no geoid / NAVD88 orthometric heights in
v1 (explicit non-goal).

## Install

```bash
pip install git+https://github.com/crieck2010/survey-crs.git
# optional TM backend (lazy; engine works standalone without it)
pip install survey-geodesy
```

## Quick start

```python
import crs

# project NB2147 (NGS) to NY Central, metres
r = crs.project(42.4329225, -76.8629327, 6534)
print(r.x, r.y)  # 226994.092 270216.779  (NGS: 226994.092 / 270216.778)

# convert between zones; datum provenance rides along
t = crs.transform_coords(226994.092, 270216.778, 6534, 6535)
print(t.x, t.y, t.unit)          # 744729.78 886536.21 ftUS
print(t.datum_path.method)       # identity

# picker
crs.zones_for_state("NY")        # 8 entries
crs.search("long island")        # EPSG:6538, 6539, ...
crs.suggest(40.76, -73.20)       # NY Long Island + UTM 18N
crs.by_epsg(6538).describe()     # full researched parameter sheet
```

CLI:

```bash
crs list --state NY
crs search "utm 18n"
crs info 6538
crs convert --from-epsg 6318 --to-epsg 6534 --lat 42.4329 --lon -76.8629
crs convert --from-epsg 6538 --to-epsg 4326 --easting 367742.490 --northing 66266.506
```

## API

Stable public API (consumed by `survey-field` v0.2.0 and `survey-suite` v0.3.0):

| Function | Purpose |
|---|---|
| `by_epsg(code)` | one `CrsEntry` by EPSG code |
| `search(query, limit=None)` | substring search over name/state/zone/EPSG/area |
| `zones_for_state(state)` | SPCS zones for a state name or abbreviation |
| `group_by_type()` | `{"spcs": [...], "utm": [...], "geographic": [...]}` |
| `suggest(lat, lon, datum="NAD83(2011)")` | zones containing the point + UTM zone |
| `project(lat, lon, epsg, h=0.0)` | geographic → CRS (`TransformResult`) |
| `unproject(x, y, epsg, h=0.0)` | CRS → geographic |
| `transform_coords(x, y, from_epsg, to_epsg, h=0.0)` | any → any, with datum provenance |
| `datum_path(from_datum, to_datum)` | `DatumPath` with accuracy metadata |
| `m_to_ftus / ftus_to_m / m_to_ft / ft_to_m` | exact unit helpers (`US_FOOT_M = 1200/3937`) |
| `backend_name()` | `"survey-geodesy"` or `"internal"` |

`CrsEntry` fields: `name, epsg, datum, kind, params, params_epsg, unit,
area_name, bbox, state, zone, source_url, notes, group`.

`TransformResult` fields: `x, y, h, unit, from_epsg, to_epsg, from_datum,
to_datum, datum_path, backend, warnings`.

## Sources

- EPSG registry via epsg.io — one citation URL per entry
  (`CrsEntry.source_url`).
- NOAA Manual NOS NGS 5, *State Plane Coordinate System of 1983*
  (https://www.ngs.noaa.gov/PUBS_LIB/ManualNOSNGS5.pdf) — SPCS definitions.
- NGS datasheets (NB2147, NB1891, DI0446) and the NOAA-hosted Seneca NY
  Watershed LiDAR Survey Report — published-coordinate validations.
- Penn State GEOG 862 (NAD83/WGS84 ~1–2 m) and NC Geodetic Survey 2011
  readjustment notes (CORS96→2011 ~2 cm) — datum accuracy metadata.

Full citations: `docs/SOURCES.md`. Datum details: `docs/DATUMS.md`.
Interop: `docs/INTEROP.md`.

## Limitations (v1)

- Datum shifts between distinct datums are **null approximations**
  (~2 m NAD83(2011)↔WGS 84 in CONUS; ~2–5 cm CORS96↔2011). Every result says
  so; do not use for survey control.
- Ellipsoidal heights only — no geoid, no NAVD88.
- Registry mirrors the EPSG database as researched 2026-09-27 (pyproj 3.8.0
  snapshot); EPSG deprecations after that date are not tracked.
- `suggest()` uses EPSG area bboxes, which are coarse near borders.

## License

MIT — see `LICENSE`.
