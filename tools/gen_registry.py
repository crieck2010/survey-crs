"""Generate src/crs/_registry_data.py from the EPSG research snapshot.

Research method (run once, 2026-09-27, NOT a runtime dependency):
    - pyproj 3.8.0 (temporary venv in /tmp/epsgresearch) queried its bundled
      EPSG database for NAD83(2011) projected CRSs whose names match the
      SPCS83 set -> tools/spcs_dump.json (222 entries).
    - Every entry's projection parameters below are copied verbatim from the
      EPSG registry via pyproj; per-entry source URLs are epsg.io/<code>.
    - WGS 84 / UTM zones 1-60 N/S are defined by EPSG:32601-32660 and
      EPSG:32701-32760 (standard UTM: k0=0.9996, FE=500000 m).
    - Geographic CRSs: EPSG:6318 (NAD83(2011)), EPSG:6783 (NAD83(CORS96)),
      EPSG:4326 (WGS 84 ensemble).

Re-run:  python3 tools/gen_registry.py
Output:  src/crs/_registry_data.py  (checked in; stdlib-only at runtime)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "spcs_dump.json")
OUT = os.path.join(HERE, "..", "src", "crs", "_registry_data.py")

USFT = 1200.0 / 3937.0          # exact US survey foot in metres
INTL_FT = 0.3048                # exact international foot in metres

STATES = [
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "South Carolina", "South Dakota",
    "West Virginia", "Rhode Island", "Puerto Rico and Virgin Is.",
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Idaho", "Illinois",
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "Ohio", "Oklahoma",
    "Oregon", "Pennsylvania", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "Wisconsin", "Wyoming",
]

KIND = {
    "Transverse Mercator": "tm",
    "Lambert Conic Conformal (2SP)": "lcc",
    "Hotine Oblique Mercator (variant A)": "hotine",
}

UNIT = {"metre": "m", "US survey foot": "ftUS", "foot": "ft"}
UNIT_TO_M = {"m": 1.0, "ftUS": USFT, "ft": INTL_FT}

NY_NOTES = {
    6534: "NY first-class zone (metres)",
    6535: "NY first-class zone (US survey feet)",
    6536: "NY official zone (metres)",
    6537: "NY official zone (US survey feet)",
    6538: "NY first-class zone (metres)",
    6539: "NY first-class zone (US survey feet)",
    6540: "NY first-class zone (metres)",
    6541: "NY first-class zone (US survey feet)",
}

PARAM_MAP = {
    "tm": {
        "Latitude of natural origin": "lat0",
        "Longitude of natural origin": "lon0",
        "Scale factor at natural origin": "k0",
        "False easting": "fe",
        "False northing": "fn",
    },
    "lcc": {
        "Latitude of false origin": "lat0",
        "Longitude of false origin": "lon0",
        "Latitude of 1st standard parallel": "lat1",
        "Latitude of 2nd standard parallel": "lat2",
        "Easting at false origin": "fe",
        "Northing at false origin": "fn",
    },
    "hotine": {
        "Latitude of projection centre": "latc",
        "Longitude of projection centre": "lonc",
        "Azimuth at projection centre": "azimuth",
        "Angle from Rectified to Skew Grid": "rectified_skew_angle",
        "Scale factor at projection centre": "kc",
        "False easting": "fe",
        "False northing": "fn",
    },
}


def split_state_zone(label):
    for st in STATES:
        if label == st or label.startswith(st + " "):
            zone = label[len(st):].strip()
            return st, zone or None
    return None, label


def convert_entry(e):
    code = e["code"]
    kind = KIND[e["method"]]
    unit = UNIT[e["unit"]]
    to_m = UNIT_TO_M[unit]
    label = e["name"].split(" / ", 1)[1]
    base = label[:-7] if label.endswith(" (ftUS)") else (label[:-5] if label.endswith(" (ft)") else label)
    state, zone = split_state_zone(base)
    params, params_epsg = {}, {}
    for p in e["params"]:
        key = PARAM_MAP[kind][p["name"]]
        params_epsg[key] = {"value": p["value"], "unit": p["unit"]}
        v = p["value"]
        if key in ("fe", "fn"):
            v = v * to_m  # normalize linear params to metres
        params[key] = v
    return {
        "name": e["name"],
        "epsg": code,
        "datum": "NAD83(2011)",
        "kind": kind,
        "params": params,
        "params_epsg": params_epsg,
        "unit": unit,
        "area_name": e["area"],
        "bbox": list(e["bbox"]),
        "state": state,
        "zone": zone,
        "source_url": "https://epsg.io/%d" % code,
        "notes": NY_NOTES.get(code, ""),
        "group": "spcs",
    }


def utm_entries():
    out = []
    for hemi, epsg0, lat0, lat1 in (("N", 32600, 0.0, 84.0), ("S", 32700, -80.0, 0.0)):
        for z in range(1, 61):
            lon0 = -180.0 + (z - 1) * 6.0 + 3.0
            out.append({
                "name": "WGS 84 / UTM zone %d%s" % (z, hemi),
                "epsg": epsg0 + z,
                "datum": "WGS 84 (G2296)",
                "kind": "utm",
                "params": {"zone": z, "hemisphere": hemi, "lon0": lon0,
                           "k0": 0.9996, "fe": 500000.0,
                           "fn": 0.0 if hemi == "N" else 10000000.0},
                "params_epsg": {},
                "unit": "m",
                "area_name": "World - UTM zone %d%s" % (z, hemi),
                "bbox": [lon0 - 3.0, lat0, lon0 + 3.0, lat1],
                "state": None,
                "zone": "%d%s" % (z, hemi),
                "source_url": "https://epsg.io/%d" % (epsg0 + z),
                "notes": "",
                "group": "utm",
            })
    return out


def geographic_entries():
    return [
        {
            "name": "NAD83(2011)",
            "epsg": 6318,
            "datum": "NAD83(2011)",
            "kind": "geographic",
            "params": {"ellipsoid": "GRS80"},
            "params_epsg": {},
            "unit": "deg",
            "area_name": "United States (USA) - CONUS, Alaska, Puerto Rico and US Virgin Islands",
            "bbox": [-179.0, 18.0, -66.0, 72.0],
            "state": None, "zone": None,
            "source_url": "https://epsg.io/6318",
            "notes": "2D geographic; ellipsoidal heights only in v1",
            "group": "geographic",
        },
        {
            "name": "NAD83(CORS96)",
            "epsg": 6783,
            "datum": "NAD83(CORS96)",
            "kind": "geographic",
            "params": {"ellipsoid": "GRS80"},
            "params_epsg": {},
            "unit": "deg",
            "area_name": "United States (USA)",
            "bbox": [-179.0, 18.0, -66.0, 72.0],
            "state": None, "zone": None,
            "source_url": "https://epsg.io/6783",
            "notes": "2D geographic; CORS realization, epoch 2002.0",
            "group": "geographic",
        },
        {
            "name": "WGS 84",
            "epsg": 4326,
            "datum": "WGS 84 (G2296)",
            "kind": "geographic",
            "params": {"ellipsoid": "WGS84"},
            "params_epsg": {},
            "unit": "deg",
            "area_name": "World",
            "bbox": [-180.0, -90.0, 180.0, 90.0],
            "state": None, "zone": None,
            "source_url": "https://epsg.io/4326",
            "notes": "WGS 84 ensemble; current operational realization G2296",
            "group": "geographic",
        },
    ]


def main():
    dump = json.load(open(SRC))
    entries = [convert_entry(e) for e in dump]
    entries += geographic_entries()
    entries += utm_entries()
    entries.sort(key=lambda r: r["epsg"])
    with open(OUT, "w") as f:
        f.write('"""Checked-in CRS registry data. Generated by tools/gen_registry.py\n')
        f.write('from the EPSG research snapshot tools/spcs_dump.json.\n\n')
        f.write('Do not edit by hand; re-run the generator. Every entry carries\n')
        f.write('its EPSG source URL for verification.\n"""\n\n')
        f.write("REGISTRY = ")
        import pprint
        f.write(pprint.pformat(entries, width=100, sort_dicts=False))
        f.write("\n")
    kinds = {}
    for r in entries:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print("wrote", OUT, "entries:", len(entries), kinds)


if __name__ == "__main__":
    main()
