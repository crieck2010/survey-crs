# Sources

Every registry entry carries its own EPSG citation in `CrsEntry.source_url`
(`https://epsg.io/<code>`). This file lists the sources behind the registry,
the projection math, the datum accuracy metadata, and the test validations.

## Registry parameters

- **EPSG registry** (via https://epsg.io, per-code pages such as
  https://epsg.io/6538): official CRS names, projection methods and
  parameters, linear units, and areas of use for all 222 NAD83(2011) SPCS83
  entries. Researched 2026-09-27 via the EPSG database bundled with
  PROJ/pyproj 3.8.0 (research tool only, not a runtime dependency; the
  snapshot is checked in at `tools/spcs_dump.json` and the generator at
  `tools/gen_registry.py`).
- **NOAA Manual NOS NGS 5**, *State Plane Coordinate System of 1983*
  (https://www.ngs.noaa.gov/PUBS_LIB/ManualNOSNGS5.pdf): the defining
  document for SPCS83 zone definitions and computation methods.
- **NYSDOT Highway Design Manual Chapter 6**, *Coordinate Systems and Datums*
  (https://www.dot.ny.gov/divisions/engineering/design/design-services/land-survey/repository/Chapter%206%20NYSDOT%20Coordinate%20Systems%20and%20Datums.pdf):
  NYSPCS zone usage, CORS datum policy; references Manual NOS NGS 5.
- **NY Laws, Chapter 605 (1995)** — statutory definition of the four NY
  SPCS zones (parallels, origins, false eastings), cross-checked against the
  EPSG parameters for 6534-6541.

## Datums

- Current operational WGS 84 realization **G2296** (effective 2024-01-07,
  aligned to ITRF2020; supersedes G2139).
- NAD83(2011) vs modern WGS 84 differ by roughly **1-2 m** across CONUS:
  Penn State GEOG 862, https://www.e-education.psu.edu/geog862/node/1804.
- NAD83(CORS96) -> NAD83(2011) shifts are centimetre-level (mean ~1.8 cm
  horizontal, ~-0.8 cm ellipsoidal height): NC Geodetic Survey, *The National
  Adjustment of 2011*,
  https://ncgs.state.nc.us/docs/2012-09-20_The_National_Adjustment_of_2011.pdf.
- US survey foot defined as exactly **1200/3937 m** (NIST Handbook 44;
  adopted for SPCS by Manual NOS NGS 5).

## Published-coordinate validations (tests/test_published.py)

- **NB2147** (TT 40 R, NY/Schuyler): NGS datasheet, NAD83(2011) ADJUSTED
  position 42 25 58.52091N 076 51 46.55757W; SPC NY Central
  N 270,216.778 / E 226,994.092 m and N 886,536.21 / E 744,729.78 ftUS.
  Retrieved live 2026-09-27 from
  https://www.ngs.noaa.gov/cgi-bin/ds_mark.prl?PidBox=NB2147.
- **NB1891** (FLISCHMAN, NY/Steuben): NGS datasheet, NAD83(2011) ADJUSTED
  42 32 07.44358N 077 29 17.91926W; SPC NY West N 282,142.939 /
  E 439,953.828 m and N 925,663.96 / E 1,443,415.18 ftUS.
  https://www.ngs.noaa.gov/cgi-bin/ds_mark.prl?PidBox=NB1891.
- **DI0446** (CENTRAL ISLIP CORS ARP, NYCI, NY/Suffolk): NGS datasheet,
  NAD83(2011) ADJUSTED 40 45 38.23676N 073 11 51.78749W; SPC NY Long Island
  N 66,266.506 / E 367,742.490 m and N 217,409.36 / E 1,206,501.82 ftUS.
  https://www.ngs.noaa.gov/cgi-bin/ds_mark.prl?PidBox=DI0446.
- **NB2147 UTM 18N** (E 346,764.059 / N 4,699,526.108): NOAA-hosted Seneca NY
  Watershed LiDAR Survey Report, control table p. 5,
  https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/9066/supplemental/Seneca_NY_Watershed_LiDAR_Survey_Report.pdf.
  Used as a projection-math check (see test docstring for the datum note).
- **Alaska zone 1 (EPSG:6394, Hotine OM)**: reference values computed with
  PROJ (pyproj 3.8.0) from the EPSG definition — the reference
  implementation, not NGS-published coordinates.

NGS datasheet values are published rounded to 0.001 m (0.01 ftUS); test
tolerances account for that rounding plus numerical projection error.
