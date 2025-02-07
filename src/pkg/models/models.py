import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Amenity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID]
    osm_id: int
    name: Optional[str]
    amenity_type: Optional[str]
    address: Optional[str]
    opening_hours: Optional[str]
    geometry: str  # Point
    updated_at: datetime = Field(default=datetime.now())
    updated_by: Optional[str] = None


class Building(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID]
    osm_id: int
    information: dict
    geometry: str  # Polygon
