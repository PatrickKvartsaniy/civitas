import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from .consts import amenity_category_map


class Amenity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    name: Optional[str]
    amenity_type: Optional[str]
    address: Optional[str]
    opening_hours: Optional[str]
    geometry: str  # GeoJSON Point as string
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    def to_geojson(self) -> Dict[str, Any]:
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
            "geometry": json.loads(self.geometry),  # Ensure it's a valid GeoJSON object
        }


class AmenityUpdate(BaseModel):
    name: Optional[str]
    amenity_type: Optional[str]
    address: Optional[str]
    opening_hours: Optional[str]
    updated_by: Optional[str]


class Building(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    information: Dict[str, Any]
    geometry: str  # GeoJSON Polygon as string
    requires_maintenance: bool
    amenity: Optional[Amenity] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    def to_geojson(self) -> Dict[str, Any]:
        # Create the base properties dictionary
        amenity_type = self.amenity.amenity_type if self.amenity else None
        if amenity_type:
            print(amenity_type)
        properties = {
            "id": str(self.id) if self.id else None,
            "osm_id": self.osm_id,
            "requires_maintenance": self.requires_maintenance,
            "updated_at": self.updated_at.isoformat(),
            "updated_by": self.updated_by,
            "amenity_category": amenity_category_map.get(amenity_type, "Residential"),
        }

        # Unpack the 'information' dictionary into the properties dictionary
        if self.information and isinstance(self.information, dict):
            properties.update(self.information)

        return {
            "type": "Feature",
            "properties": properties,
            "geometry": json.loads(self.geometry),  # Ensure it's a valid GeoJSON object
        }


class BuildingUpdate(BaseModel):
    information: Dict[str, Any]
    requires_maintenance: bool
    updated_by: Optional[str]
    amenity_id: Optional[uuid.UUID]
