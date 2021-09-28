from dms2dec.dms_convert import dms2dec
from geojson import Polygon, Feature, FeatureCollection
from geopy import distance
from math import sqrt
import argparse
import json
import simplekml

def calculate_rect(lat, lon, dist):
    center = (lat, lon, 0)

    # calculate distance from center to edge
    dist = dist / 2

    # Bearing in degrees: 0 – North, 90 – East, 180 – South, 270 or -90 – West.
    dist = distance.distance(kilometers=sqrt(dist ** 2 + dist ** 2))

    south_west = dist.destination(center, 90 + 45)
    north_west = dist.destination(center, 0 + 45)
    north_east = dist.destination(center, 0 - 45)
    south_east = dist.destination(center, 180 + 45)

    # flip lat/long to lon/lat (geojson standard)
    south_west_lonlat = south_west[:2][::-1]
    south_east_lonlat = south_east[:2][::-1]
    north_east_lonlat = north_east[:2][::-1]
    north_west_lonlat = north_west[:2][::-1]

    return [
        south_west_lonlat,
        south_east_lonlat,
        north_east_lonlat,
        north_west_lonlat,
        south_west_lonlat
    ]

parser = argparse.ArgumentParser(
    description='Create a rectangle at a geo position.'
    )

parser.add_argument('lat', type=str, help='Latitude')
parser.add_argument('lon', type=str, help='Longitude')
parser.add_argument('dist', type=float, help='Distance', default=1000)
parser.add_argument(
        '--format',
        default="kml",
        help='output format (default: kml)'
        )
parser.add_argument('--degrees', action='store_true')

args = parser.parse_args()

if args.degrees is True:
    args.lat = dms2dec(args.lat)
    args.lon = dms2dec(args.lon)

coordinates = calculate_rect(args.lat, args.lon, args.dist)

if args.format == "kml":
    kml = simplekml.Kml()
    kml.newpolygon(name="Survey", outerboundaryis=coordinates)
    print(kml.kml())
else:
    # create geojson
    poly = Polygon([coordinates])
    rectangle = Feature(geometry=poly)
    collection = FeatureCollection([rectangle])
    print(json.dumps({"type": "FeatureCollection"} | collection))  # paste collection into geoman.io without quotes
