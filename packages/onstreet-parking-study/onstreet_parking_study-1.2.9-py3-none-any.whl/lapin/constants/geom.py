from pyproj import CRS

UNIVERSAL_CRS = CRS.from_epsg(3857)
DEFAULT_CRS = CRS.from_epsg(4326)
MONTREAL_CRS = CRS.from_epsg(32188)

EARTH_RADIUS = 6371000
