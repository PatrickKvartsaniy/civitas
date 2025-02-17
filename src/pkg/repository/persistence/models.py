import json
import uuid

import shapely
from geoalchemy2.shape import from_shape
from shapely.geometry.geo import shape, mapping
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    JSON,
    ForeignKey,
    func,
    DateTime,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID

from geoalchemy2 import Geometry
from sqlalchemy.orm import validates, relationship

from src.pkg.infrastructure.postgresql import Base
from src.pkg.models import Building as BuildingSchema, Amenity as AmenitySchema


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    username = Column(String, unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=True)


class Amenity(Base):
    __tablename__ = "amenities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    osm_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=True)
    amenity_type = Column(String, nullable=True)
    amenity_category = Column(String, nullable=True)
    address = Column(String, nullable=True)
    opening_hours = Column(String, nullable=True)
    geometry = Column(Geometry("POINT", srid=4326), nullable=False)
    updated_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        onupdate=func.now(),
        server_default=func.now(),
    )
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    @validates("geometry")
    def validate_geometry(self, key, value):
        if isinstance(value, str):
            try:  # Handle potential JSON decoding errors
                geojson_dict = json.loads(value)
                point = shape(geojson_dict)
                return from_shape(point, srid=4326)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid GeoJSON: {e}")  # Re-raise as ValueError
        return value

    def as_dto(self) -> AmenitySchema:
        as_dict = {
            "id": self.id,
            "osm_id": self.osm_id,
            "name": self.name,
            "amenity_type": self.amenity_type,
            "amenity_category": self.amenity_category,
            "address": self.address,
            "opening_hours": self.opening_hours,
            "geometry": shapely.from_wkb(self.geometry.data).wkt,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
        }
        return AmenitySchema.model_validate(as_dict)


class Building(Base):
    __tablename__ = "buildings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    osm_id = Column(BigInteger, unique=True, nullable=False)
    information = Column(JSON, nullable=False)  # Stores metadata as a JSON object
    geometry = Column(
        Geometry("POLYGON", srid=4326), nullable=False
    )  # SRID in column definition
    requires_maintenance = Column(
        Boolean, default=False, nullable=False, server_default="false"
    )

    amenity = Column(UUID(as_uuid=True), ForeignKey("amenities.id"), nullable=True)
    amenity_rel = relationship("Amenity")

    updated_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        onupdate=func.now(),
        server_default=func.now(),
    )
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    @validates("geometry")
    def validate_geometry(self, key, value):
        if isinstance(value, str):
            try:  # Handle potential JSON decoding errors
                geojson_dict = json.loads(value)
                polygon = shape(geojson_dict)
                return from_shape(polygon, srid=4326)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid GeoJSON: {e}")  # Re-raise as ValueError
        return value

    def as_dto(self) -> BuildingSchema:
        as_dict = {
            "id": self.id,
            "osm_id": self.osm_id,
            "information": self.information,
            "geometry": shapely.from_wkb(self.geometry.data).wkt,
            "requires_maintenance": self.requires_maintenance,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
            "amenity": self.amenity_rel.as_dto() if self.amenity_rel else None,
        }
        return BuildingSchema.model_validate(as_dict)
