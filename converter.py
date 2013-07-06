"""
Simple stupid converter to convert JSON files from MBTA website to GeoJSON files
"""

import os
import os.path
from decimal import Decimal
import simplejson as json
import re
import unicodedata
from collections import defaultdict

stops = defaultdict(dict)
routes = defaultdict(dict)
areas = {
    "CAMBR": "cambridge",
    "NEWTO": "newton",
    "BRIGH": "brighton",
    "CHRLS": "charlestown",
    "BROOK": "brookline",
    "BRKLN": "brookline",
    "BOSTO": "boston",
    "REVER": "revere",
    "BRAIN": "braintree",
    "SOMVL": "somerville",
    "MALDE": "malden",
    "QUINC": "quincy",
    "MILTO": "milton",
    "JAMAI": "jamaica-plain",
}

def slugify(string):
    return re.sub(r'[-\s]+', '-',
            unicode(
                re.sub(r'[^\w\s-]', '', string)
                .strip()
                .lower()))

dirname = "unformatted"
for name in os.listdir(dirname):
    print(name)
    obj = json.load(open(os.path.join(dirname, name)))
    name_obj = obj["Name"][0]
    line_id = name_obj["line"].lower()
    route = routes[line_id]
    if not "points" in route:
        route["points"] = []
    if not "stops" in route:
        route["stops"] = []
    route["name"] = name_obj["LineName"]
    route["directions"] = name_obj["directions"].split(",")

    for stop_info in obj["Stop"]:
        name = stop_info["StopName"]
        point = [Decimal(stop_info["Long"]), Decimal(stop_info["Lat"])]
        route["points"].append(point)
        slug = slugify(name)
        if name != "Point":
            stop = stops[slug]
            stop["name"] = name
            stop["point"] = point
            stop["area"] = areas[stop_info["Area"]]
            if not "lines" in stop:
                stop["lines"] = set()
            stop["lines"].add(stop_info["LineName"])
            stop["lines"].add(line_id)
            route["stops"].append(slug)


stop_features = []
for slug, stop in stops.iteritems():
    stop_features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": stop["point"]
        },
        "properties": {
            "id": slug,
            "name": stop["name"],
            "area": stop["area"],
            "lines": list(stop["lines"]),
        }
    })

route_features = []
for slug, route in routes.iteritems():
    route_features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": route["points"],
        },
        "properties": {
            "id": slug,
            "name": route["name"],
            "directions": route["directions"],
            "stops": route["stops"],
        }
    })

with open("stops.geojson", "w") as stops_f:
    stops_f.write(json.dumps({
        "type": "FeatureCollection",
        "features": stop_features,
    }, use_decimal=True, indent=2))

with open("routes.geojson", "w") as stops_f:
    stops_f.write(json.dumps({
        "type": "FeatureCollection",
        "features": route_features,
    }, use_decimal=True, indent=2))
