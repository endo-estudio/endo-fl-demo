import zipfile
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict

KMZ_PATH = "KMZ Base Completo.kmz"
OUTPUT_PATH = "assets/geojson/capas-base.geojson"
LOG_PATH = "conversion-log.txt"
NS = "http://www.opengis.net/kml/2.2"


def tag(name):
    return f"{{{NS}}}{name}"


def parse_coords(text):
    coords = []
    for part in text.strip().split():
        vals = part.split(",")
        lng, lat = float(vals[0]), float(vals[1])
        alt = float(vals[2]) if len(vals) > 2 else 0
        coords.append([lng, lat, alt])
    return coords


def placemark_to_feature(pm):
    name = pm.findtext(tag("name"), "").strip()
    desc = pm.findtext(tag("description"), "").strip()
    props = {"name": name, "description": desc}

    # Extended data
    ed = pm.find(tag("ExtendedData"))
    if ed is not None:
        for data in ed.findall(tag("Data")):
            key = data.get("name", "")
            val = data.findtext(tag("value"), "")
            props[key] = val
        for sdata in ed.findall(tag("SchemaData")):
            for sd in sdata.findall(tag("SimpleData")):
                props[sd.get("name", "")] = sd.text or ""

    geometry = None

    point = pm.find(tag("Point"))
    if point is not None:
        raw = point.findtext(tag("coordinates"), "")
        coords = parse_coords(raw)
        geometry = {"type": "Point", "coordinates": coords[0]}

    linestring = pm.find(tag("LineString"))
    if linestring is not None:
        raw = linestring.findtext(tag("coordinates"), "")
        geometry = {"type": "LineString", "coordinates": parse_coords(raw)}

    polygon = pm.find(tag("Polygon"))
    if polygon is not None:
        outer = polygon.find(f".//{tag('outerBoundaryIs')}/{tag('LinearRing')}/{tag('coordinates')}")
        rings = [parse_coords(outer.text)] if outer is not None else []
        for inner in polygon.findall(f".//{tag('innerBoundaryIs')}/{tag('LinearRing')}/{tag('coordinates')}"):
            rings.append(parse_coords(inner.text))
        geometry = {"type": "Polygon", "coordinates": rings}

    if geometry is None:
        return None

    return {"type": "Feature", "geometry": geometry, "properties": props}


def collect_placemarks(element, features, folder_name=""):
    for folder in element.findall(tag("Folder")):
        fname = folder.findtext(tag("name"), folder_name).strip()
        collect_placemarks(folder, features, fname)
    for pm in element.findall(tag("Placemark")):
        feat = placemark_to_feature(pm)
        if feat:
            feat["properties"]["_folder"] = folder_name
            features.append(feat)


with zipfile.ZipFile(KMZ_PATH, "r") as z:
    kml_bytes = z.read("doc.kml")

root = ET.fromstring(kml_bytes)
document = root.find(tag("Document")) or root

features = []
collect_placemarks(document, features)

geojson = {"type": "FeatureCollection", "features": features}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

# Stats for log
geom_counts = defaultdict(int)
prop_keys = set()
folders = set()
for feat in features:
    geom_counts[feat["geometry"]["type"]] += 1
    prop_keys.update(feat["properties"].keys())
    folders.add(feat["properties"].get("_folder", ""))

log_lines = [
    f"Fecha de conversión : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"Archivo fuente      : {KMZ_PATH}",
    f"Archivo destino     : {OUTPUT_PATH}",
    f"Total de features   : {len(features)}",
    "",
    "Tipos de geometría:",
]
for gtype, count in sorted(geom_counts.items()):
    log_lines.append(f"  {gtype}: {count}")

log_lines += [
    "",
    "Capas / Folders:",
]
for folder in sorted(folders):
    log_lines.append(f"  {folder or '(raíz)'}")

log_lines += [
    "",
    "Propiedades encontradas:",
]
for key in sorted(prop_keys):
    log_lines.append(f"  {key}")

log_text = "\n".join(log_lines) + "\n"
with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write(log_text)

print(log_text)
