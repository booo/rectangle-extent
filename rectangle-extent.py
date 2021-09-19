from geojson import Polygon, Feature, FeatureCollection
from geopy import distance
import argparse
import json
import simplekml


def calculate_rect(lat, lon, dist):
    # Calculate Rectangle with south west in Berlin with width 10km  and height 2km 
    south_west = (lat, lon, 0)
    width_in_km = dist
    height_in_km = dist

    # Bearing in degrees: 0 – North, 90 – East, 180 – South, 270 or -90 – West.
    bearing_east = 90
    bearing_north = 0

    south_east = distance.distance(kilometers=width_in_km).destination(south_west, bearing_east)
    north_east = distance.distance(kilometers=height_in_km).destination(south_east, bearing_north)
    north_west = distance.distance(kilometers=height_in_km).destination(south_west, bearing_north)


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

parser.add_argument('lat', type=float, help='Latitude')
parser.add_argument('lon', type=float, help='Longitude')
parser.add_argument('dist', type=float, help='Distance', default=1000)
parser.add_argument(
        '--format',
        default="kml",
        help='output format (default: kml)'
        )

args = parser.parse_args()

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
