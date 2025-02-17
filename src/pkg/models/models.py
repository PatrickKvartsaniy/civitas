import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict
from shapely.wkt import loads
from shapely.geometry import mapping

from .enums import amenity_category_map


class Amenity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    name: Optional[str]
    amenity_type: Optional[str]
    amenity_category: Optional[str] = ""
    address: Optional[str]
    opening_hours: Optional[str]
    geometry: str
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    def populate_category(self):
        """Populates the amenity_category based on amenity_type."""
        if self.amenity_type:
            self.amenity_category = amenity_category_map.get(self.amenity_type)

    @property
    def shapely_geometry(self):
        """Converts the stored WKT geometry to a Shapely object."""
        return loads(self.geometry)

    def as_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "properties": {
                "id": str(self.id) if self.id else None,
                "osm_id": self.osm_id,
                "name": self.name,
                "amenity_type": self.amenity_type,
                "address": self.address,
                "opening_hours": self.opening_hours,
                "updated_at": self.updated_at.isoformat(),
                "updated_by": self.updated_by,
            },
            "geometry": mapping(self.shapely_geometry),  # Convert Shapely to GeoJSON
        }


class Building(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    information: Dict[str, Any]
    geometry: str  # Store as WKT
    requires_maintenance: bool
    amenity: Optional[Amenity] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    @property
    def shapely_geometry(self):
        """Converts the stored WKT geometry to a Shapely object."""
        return loads(self.geometry)

    def as_geojson(self) -> Dict[str, Any]:
        # Create the base properties dictionary
        amenity_category = self.amenity.amenity_category if self.amenity else None
        if not amenity_category:
            amenity_category = amenity_category_map.get(
                self.information.get("amenity"), "Residential"
            )

        properties = {
            "id": str(self.id) if self.id else None,
            "osm_id": self.osm_id,
            "requires_maintenance": self.requires_maintenance,
            "updated_at": self.updated_at.isoformat(),
            "updated_by": self.updated_by,
            "amenity_category": amenity_category,
        }

        return {
            "type": "Feature",
            "properties": properties,
            "geometry": mapping(self.shapely_geometry),  # Convert Shapely to GeoJSON
        }


class AmenityUpdate(BaseModel):
    name: Optional[str]
    amenity_type: Optional[str]
    address: Optional[str]
    opening_hours: Optional[str]
    updated_by: Optional[str]


class BuildingUpdate(BaseModel):
    information: Dict[str, Any]
    requires_maintenance: bool
    updated_by: Optional[str]
    amenity_id: Optional[uuid.UUID]


class RouteGeometryDistance(BaseModel):
    geometry: str  # GeoJSON LineString as string
    distance: float
    duration: float


class ClosestAmenityResponse(BaseModel):
    amenity: Optional[Amenity]
    route: Optional[RouteGeometryDistance]
