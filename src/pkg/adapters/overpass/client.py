from typing import List

import overpy

from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from shapely.io import to_geojson

from src.pkg.models.models import Amenity, Building


class Client:
    def __init__(self):
        """
        Initialize the Overpass API Wrapper.
        """
        self.api = overpy.Overpass()

    async def extract_buildings(self, bounding_box: tuple) -> List[Building]:
        """
        Fetch all buildings and their metadata within the bounding box.

        :return: Overpy result object with building data.
        """
        query = f"""
        [out:json];
        way["building"]{bounding_box};
        (._;>;);
        out body;
        """

        response = self.api.query(query)

        buildings = []
        for way in response.ways:
            nodes = [(node.lon, node.lat) for node in way.nodes]
            building = Building(
                osm_id=way.id,
                information=way.tags,
                geometry=to_geojson(Polygon(nodes)),
            )
            buildings.append(building)
        return buildings

    async def extract_amenities(self, bounding_box: tuple) -> List[Amenity]:
        """
        Fetch all amenities (restaurants, cafés, banks, pharmacies, shops, and offices) within the bounding box.
        """
        query = f"""
        [out:json];
        (
          node["amenity"~"restaurant|cafe|bank|pharmacy"]({bounding_box[0]}, {bounding_box[1]}, {bounding_box[2]}, {bounding_box[3]});
          node["shop"]({bounding_box[0]}, {bounding_box[1]}, {bounding_box[2]}, {bounding_box[3]});
          node["office"]({bounding_box[0]}, {bounding_box[1]}, {bounding_box[2]}, {bounding_box[3]});
        );
        out body;
        """

        try:
            response = self.api.query(query)
        except Exception as e:
            raise RuntimeError(f"Overpass query failed: {e}")

        amenities = []
        for node in response.nodes:
            tags = node.tags
            amenity = Amenity(
                osm_id=node.id,
                name=tags.get("name"),
                amenity_type=tags.get("amenity"),
                address=tags.get("addr:street"),
                opening_hours=tags.get("opening_hours"),
                geometry=to_geojson(Point(float(node.lon), float(node.lat))),
            )
            amenities.append(amenity)

        return amenities

    async def extract_admin_boundaries(self, bounding_box: tuple) -> List[dict]:
        """
        Fetch administrative boundaries (country, state, city, etc.) within the bounding box.

        :param bounding_box: A tuple (min_lat, min_lon, max_lat, max_lon) defining the area.
        :return: A list of dictionaries containing administrative boundary details.
        """
        query = f"""
        [out:json];
        (
        relation["boundary"="administrative"]({bounding_box[0]}, {bounding_box[1]}, {bounding_box[2]}, {bounding_box[3]});
        );
        out body;
        """

        try:
            response = self.api.query(query)
        except Exception as e:
            raise RuntimeError(f"Overpass query failed: {e}")

        boundaries = []
        for relation in response.relations:
            boundary = {
                "osm_id": relation.id,
                "name": relation.tags.get("name"),
                "admin_level": relation.tags.get("admin_level"),
                "geometry": to_geojson(Polygon([(node.lon, node.lat) for node in relation.members if node.role == "outer"])),
            }
            boundaries.append(boundary)

        return boundaries
