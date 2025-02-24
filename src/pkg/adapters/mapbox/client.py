import aiohttp
import json
import urllib.parse
from typing import Optional
from shapely.geometry import shape, Polygon
import logging

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, access_token: str):
        self.access_token = access_token

    async def get_static_image(
        self,
        geojson_str: str,
        zoom: int = 18,
        size: str = "800x600",
    ) -> Optional[bytes]:
        """
        Generates a Mapbox static image from a GeoJSON polygon and returns it as image bytes.

        Args:
            geojson_str: A GeoJSON string representing the polygon.
            zoom: The zoom level of the map.
            size: The size of the image in pixels (e.g., "600x400").

        Returns:
            The image bytes if the image was successfully retrieved, otherwise None.
        """
        if not geojson_str:
            raise ValueError("Polygon GeoJSON cannot be empty.")

        try:
            geojson = json.loads(geojson_str)
        except json.JSONDecodeError as e:
            logger.error("Invalid GeoJSON provided: %s", e)
            return None

        try:
            polygon: Polygon = shape(
                geojson["geometry"]
            )  # This is where the error occurs
        except Exception as e:
            logger.error("Error creating polygon from GeoJSON: %s", e)
            return None

        # Calculate the center of the polygon
        center = (polygon.centroid.x, polygon.centroid.y)

        # Re-serialize GeoJSON to ensure proper formatting
        geojson_encoded = urllib.parse.quote(json.dumps(geojson))

        # Construct the API URL
        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"geojson({geojson_encoded})/{center[0]},{center[1]},{zoom}/{size}"
            f"?access_token={self.access_token}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    image_bytes = await response.read()
                    logger.info("Map image retrieved successfully.")
                    return image_bytes
        except aiohttp.ClientResponseError as e:
            logger.error(
                "HTTP Error getting Mapbox static image: %s - %s", e.status, e.message
            )
        except Exception as e:
            logger.error("Unexpected error: %s", e)

        return None
