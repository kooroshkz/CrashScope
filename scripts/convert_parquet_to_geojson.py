from pathlib import Path
import pandas as pd
import json
import sys

try:
    from pyproj import Transformer
    HAVE_PYPROJ = True
except Exception:
    HAVE_PYPROJ = False

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "datasets" / "RawData" / "accidents_2022_2024_full.parquet"


def main():
    if not TARGET.exists():
        print(f"Target parquet not found: {TARGET}")
        sys.exit(1)

    print(f"Loading parquet: {TARGET}")
    df = pd.read_parquet(TARGET)

    lon_min = float(df['lon'].min())
    lon_max = float(df['lon'].max())
    lat_min = float(df['lat'].min())
    lat_max = float(df['lat'].max())
    if not (-180 <= lon_min <= 180 and -180 <= lon_max <= 180 and -90 <= lat_min <= 90 and -90 <= lat_max <= 90):
        if HAVE_PYPROJ:
            print("Detected non-WGS84 coordinates — transforming from EPSG:28992 to EPSG:4326 using pyproj")
            transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
            lons = df['lon'].astype(float).to_numpy()
            lats = df['lat'].astype(float).to_numpy()
            lon_wgs, lat_wgs = transformer.transform(lons, lats)
            df['lon'] = lon_wgs
            df['lat'] = lat_wgs
        else:
            print("Coordinates appear projected (not WGS84). Install 'pyproj' to enable reprojection:")
            print("  pip install pyproj")
            # continue without transforming; output may be in wrong CRS

    if 'lat' not in df.columns or 'lon' not in df.columns:
        alt_lat = None
        alt_lon = None
        for c in df.columns:
            if c.lower().startswith('lat'):
                alt_lat = c
            if c.lower().startswith('lon') or c.lower().startswith('lng') or c.lower().startswith('long'):
                alt_lon = c
        if alt_lat and alt_lon:
            df = df.rename(columns={alt_lat: 'lat', alt_lon: 'lon'})
        else:
            print("Could not find latitude/longitude columns (expected 'lat' and 'lon').")
            print("Available columns:\n", list(df.columns))
            sys.exit(1)

    KEEP_FIELDS = [
        'verkeersongeval_afloop',
        'jaar_ongeval',
        'aantal_partijen',
        'maximum_snelheid',
        'lichtgesteldheid',
        'wegdek',
    ]

    df = df.dropna(subset=['lat', 'lon'])

    MAX_POINTS = 150_000
    total = len(df)
    if total > MAX_POINTS:
        print(f"Dataset large ({total} rows) — downsampling to {MAX_POINTS} rows for browser performance...")
        df = df.sample(n=MAX_POINTS, random_state=42).reset_index(drop=True)

    features = []
    for _, row in df.iterrows():
        try:
            lat = float(row['lat'])
            lon = float(row['lon'])
        except Exception:
            continue

        lon_r = round(lon, 5)
        lat_r = round(lat, 5)

        props = {}
        for c in KEEP_FIELDS:
            val = row.get(c) if c in row.index else None
            props[c] = (None if pd.isna(val) else val)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon_r, lat_r]},
            "properties": props,
        })

    geo = {"type": "FeatureCollection", "features": features}

    out_dir = Path(__file__).resolve().parents[1] / "docs" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "accidents_2022_2024_full.geojson"
    print(f"Writing {len(features)} features to {out_file}")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(geo, f)

    print("Done.")


if __name__ == '__main__':
    main()
