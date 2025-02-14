import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


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
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "properties": {
                "id": str(self.id) if self.id else None,
                "osm_id": self.osm_id,
                "information": self.information,
            },
            "geometry": json.loads(self.geometry),  # Ensure it's a valid GeoJSON object
        }


class BuildingUpdate(BaseModel):
    information: Dict[str, Any]
    requires_maintenance: bool
    updated_by: Optional[str]


class BuildingWithFunction(Building):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    osm_id: int
    information: Dict[str, Any]
    geometry: str

    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "properties": {
                "id": str(self.id) if self.id else None,
                "osm_id": self.osm_id,
                "information": self.information,
            },
            "geometry": json.loads(self.geometry),  # Ensure it's a valid GeoJSON object
        }
