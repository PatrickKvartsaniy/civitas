import json
import uuid

import shapely
from geoalchemy2.shape import from_shape
from shapely.geometry.geo import shape, mapping
from sqlalchemy import Column, BigInteger, String, JSON, ForeignKey, func, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID

from geoalchemy2 import Geometry
from sqlalchemy.orm import validates

from src.pkg.infrastructure.postgresql import Base
from src.pkg.models import Building as BuildingSchema, Amenity as AmenitySchema, AdminBoundary as AdminBoundarySchema


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
    address = Column(String, nullable=True)
    opening_hours = Column(String, nullable=True)
    geometry = Column(Geometry("POINT"), nullable=False)  # Geometry column for points
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    @validates("geometry")
    def validate_geometry(self, key, value):
        """
        Converts GeoJSON input to WKT before storing it in the database.
        """
        if isinstance(value, str):  # Assuming it's a GeoJSON string
            geojson_dict = json.loads(value)
            point = shape(geojson_dict)  # Convert GeoJSON to Shapely Polygon
            return from_shape(point, srid=4326)  # Convert to WKT with SRID
        return value

    def as_dto(self) -> AmenitySchema:
        as_dict = {
            "id": self.id,
            "osm_id": self.osm_id,
            "name": self.name,
            "amenity_type": self.amenity_type,
            "address": self.address,
            "opening_hours": self.opening_hours,
            "geometry": geometry_to_geojson(self.geometry),
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
        Geometry("POLYGON"), nullable=False
    )  # Geometry column for polygons

    @validates("geometry")
    def validate_geometry(self, key, value):
        """
        Converts GeoJSON input to WKT before storing it in the database.
        """
        if isinstance(value, str):  # Assuming it's a GeoJSON string
            geojson_dict = json.loads(value)
            polygon = shape(geojson_dict)  # Convert GeoJSON to Shapely Polygon
            return from_shape(polygon, srid=4326)  # Convert to WKT with SRID
        return value

    def as_dto(self) -> BuildingSchema:
        as_dict = {
            "id": self.id,
            "osm_id": self.osm_id,
            "information": self.information,
            "geometry": geometry_to_geojson(self.geometry),
        }
        return BuildingSchema.model_validate(as_dict)

class AdminBoundary(Base):
    __tablename__ = "admin_boundaries"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    osm_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=True)
    admin_level = Column(Integer, nullable=True)
    geometry = Column(Geometry("POLYGON"), nullable=False)

    @validates("geometry")
    def validate_geometry(self, key, value):
        """
        Converts GeoJSON input to WKT before storing it in the database.
        """
        if isinstance(value, str):  # Assuming it's a GeoJSON string
            geojson_dict = json.loads(value)
            polygon = shape(geojson_dict)  # Convert GeoJSON to Shapely Polygon
            return from_shape(polygon, srid=4326)  # Convert to WKT with SRID
        return value

    def as_dto(self) -> AdminBoundarySchema:
        as_dict = {
            "id": self.id,
            "osm_id": self.osm_id,
            "name": self.name,
            "admin_level": self.admin_level,
            "geometry": geometry_to_geojson(self.geometry),
        }
        return AdminBoundary.model_validate(as_dict)

def geometry_to_geojson(geometry):
    """
    Convert a WKBElement geometry to a GeoJSON string.
    """
    geom = mapping(shapely.from_wkb(str(geometry)))
    return json.dumps(geom)
