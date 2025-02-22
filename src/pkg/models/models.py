import orjson  # Faster JSON serialization
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from shapely.wkt import loads

from .enums import amenity_category_map


class GeoJSONable(BaseModel):
    """Base class for models that can be converted to GeoJSON."""

    def __as_geojson_string__(self, properties: Dict[str, Any]) -> str:
        """
        Converts a model to a GeoJSON string using fast serialization.
        """
        return orjson.dumps(self.__as_geojson__(properties)).decode()

    def __as_geojson__(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a model to a valid GeoJSON feature.
        """
        shapely_geom = self.shapely_geometry
        if not shapely_geom:
            raise ValueError("Invalid or missing geometry")

        geometry_type = shapely_geom.geom_type

        # Optimized coordinate extraction
        if geometry_type == "Polygon":
            exterior = list(shapely_geom.exterior.coords)
            interiors = (
                [list(ring.coords) for ring in shapely_geom.interiors]
                if shapely_geom.interiors
                else []
            )
            coordinates = [exterior] + interiors

        elif geometry_type == "MultiPolygon":
            coordinates = []
            for polygon in shapely_geom.geoms:
                exterior = list(polygon.exterior.coords)
                interiors = (
                    [list(ring.coords) for ring in polygon.interiors]
                    if polygon.interiors
                    else []
                )
                coordinates.append([exterior] + interiors)

        elif geometry_type in {"LineString", "MultiLineString"}:
            coordinates = [
                list(geom.coords)
                for geom in getattr(shapely_geom, "geoms", [shapely_geom])
            ]

        elif geometry_type in {"Point", "MultiPoint"}:
            if geometry_type == "Point":
                coordinates = list(shapely_geom.coords[0])
            else:
                coordinates = [list(point.coords[0]) for point in shapely_geom.geoms]

        else:
            raise ValueError(f"Unsupported geometry type: {geometry_type}")

        return {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": geometry_type,
                "coordinates": coordinates,
            },
        }


class Amenity(GeoJSONable):
    """Represents an amenity in the system."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    name: Optional[str]
    amenity_type: Optional[str]
    amenity_category: Optional[str] = ""
    address: Optional[str]
    opening_hours: Optional[str]
    geometry: str  # WKT representation of the geometry
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    def populate_category(self):
        """Populates the `amenity_category` based on `amenity_type`."""
        self.amenity_category = amenity_category_map.get(self.amenity_type, "Other")

    @property
    def shapely_geometry(self):
        """Converts the stored WKT geometry to a Shapely object."""
        try:
            return loads(self.geometry)
        except Exception as e:
            raise ValueError(f"Invalid WKT geometry: {e}")

    def get_properties(self) -> Dict[str, Any]:  # Consistent method name
        """Returns the properties of the amenity."""
        return {
            "id": str(self.id) if self.id else None,
            "osm_id": self.osm_id,
            "name": self.name,
            "amenity_type": self.amenity_type,
            "amenity_category": self.amenity_category,
            "address": self.address,
            "opening_hours": self.opening_hours,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }

    def as_geojson_string(self) -> str:  # Consistent method name
        """Returns the amenity as a GeoJSON string."""
        properties = self.get_properties()
        return super().__as_geojson_string__(properties)

    def as_geojson(self) -> Dict[str, Any]:  # Consistent method name
        """Returns the amenity as a GeoJSON feature."""
        properties = self.get_properties()
        return super().__as_geojson__(properties)


class Building(GeoJSONable):
    """Represents a building in the system."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    information: Dict[str, Any]
    geometry: str  # Store as WKT
    height: Optional[int] = None
    requires_maintenance: bool
    amenity: Optional[Amenity] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    @property
    def shapely_geometry(self):
        """Converts the stored WKT geometry to a Shapely object."""
        try:
            return loads(self.geometry)
        except Exception as e:
            raise ValueError(f"Invalid WKT geometry: {e}")

    def get_properties(self) -> Dict[str, Any]:
        """Returns the properties of the building."""

        amenity_category = self.amenity.amenity_category if self.amenity else None
        if not amenity_category:
            amenity_category = amenity_category_map.get(
                self.information.get("amenity"), "Residential"
            )
        return {
            "id": str(self.id) if self.id else None,
            "osm_id": self.osm_id,
            "requires_maintenance": self.requires_maintenance,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "amenity_category": amenity_category,
            "height": self.height,
            "information": self.information,
        }

    def as_geojson_string(self) -> str:
        """Returns the building as a GeoJSON string."""
        properties = self.get_properties()
        return super().__as_geojson_string__(properties)

    def as_geojson(self) -> Dict[str, Any]:
        """Returns the building as a GeoJSON feature."""
        properties = self.get_properties()
        return super().__as_geojson__(properties)


# Utility Models for Updates & Responses
class AmenityUpdate(BaseModel):
    """Update model for amenity data."""

    name: Optional[str]
    amenity_type: Optional[str]
    address: Optional[str]
    opening_hours: Optional[str]
    updated_by: Optional[str]


class BuildingUpdate(BaseModel):
    """Update model for building data."""

    information: Dict[str, Any]
    requires_maintenance: bool
    updated_by: Optional[str]


class RouteGeometryDistance(BaseModel):
    """Stores route geometry, distance, and duration."""

    geometry: str  # GeoJSON LineString as a string
    distance: float
    duration: float


class ClosestAmenityResponse(BaseModel):
    """Response model for closest amenity search."""

    amenity: str  # Amenity as GeoJSON
    route: RouteGeometryDistance
