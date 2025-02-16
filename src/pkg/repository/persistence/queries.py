import json
import uuid
from datetime import datetime
from typing import Optional, List

from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sqlalchemy.future import select
from sqlalchemy import func

from src.pkg.infrastructure.postgresql import DatabaseSessionManager
from src.pkg.models import Amenity, Building, AmenityUpdate, BuildingUpdate

from .models import (
    Amenity as AmenityModel,
    Building as BuildingModel,
)


class PersistenceRepository:
    def __init__(self, db: DatabaseSessionManager):
        self.db = db

    async def load_amenity(
        self,
        osm_id: int,
        name: Optional[str],
        amenity_type: Optional[str],
        address: Optional[str],
        opening_hours: Optional[str],
        geometry: str,
        updated_at: datetime,
        updated_by: Optional[uuid.UUID] = None,
    ):
        """
        Insert or update an amenity into the database.
        """
        async with self.db.session() as session:
            geo = from_shape(shape(json.loads(geometry)), srid=4326)
            amenity = AmenityModel(
                id=uuid.uuid4(),
                osm_id=osm_id,
                name=name,
                amenity_type=amenity_type,
                address=address,
                opening_hours=opening_hours,
                geometry=geo,
                updated_at=updated_at,
                updated_by=updated_by,
            )
            session.add(amenity)
            await session.commit()

    async def get_amenities(self) -> List[Amenity]:
        """
        Retrieve all amenities.
        """
        async with self.db.session() as session:
            result = await session.execute(select(AmenityModel))
            amenities_orm = result.scalars().all()

            amenities_schema = []
            for amenity_orm in amenities_orm:
                amenities_schema.append(amenity_orm.as_dto())
            return amenities_schema

    async def update_amenity_name(self, amenity_id: uuid.UUID, new_name: str):
        """
        Update the name of an amenity.
        """
        async with self.db.session() as session:
            amenity = await session.get(Amenity, amenity_id)
            if amenity:
                amenity.name = new_name
                await session.commit()

    async def update_amenity(self, amenity_id: uuid.UUID, update: AmenityUpdate):
        """
        Update the metadata (information field) of an amenity.
        """
        async with self.db.session() as session:
            amenity = await session.get(Amenity, amenity_id)
            if amenity:
                amenity.name = update.name
                amenity.amenity_type = update.amenity_type
                amenity.address = update.address
                amenity.opening_hours = update.opening_hours
                amenity.updated_at = datetime.now()
                amenity.updated_by = update.updated_by
                await session.commit()

    async def delete_amenity(self, amenity_id: uuid.UUID):
        """
        Delete an amenity by ID.
        """
        async with self.db.session() as session:
            amenity = await session.get(Amenity, amenity_id)
            if amenity:
                await session.delete(amenity)
                await session.commit()

    async def load_building(self, osm_id: int, metadata: dict, geometry: str):
        """
        Insert a new building into the database.
        """
        async with self.db.session() as session:
            geo = from_shape(shape(json.loads(geometry)), srid=4326)
            building = BuildingModel(
                id=uuid.uuid4(),
                osm_id=osm_id,
                information=metadata,
                geometry=geo,
            )
            session.add(building)
            await session.commit()

    async def get_buildings(self) -> List[Building]:
        async with self.db.session() as session:
            result = await session.execute(select(BuildingModel))  # Query ORM Model
            buildings_orm = result.scalars().all()  # Get list of ORM objects

            buildings_schema = []
            for building_orm in buildings_orm:
                buildings_schema.append(building_orm.as_dto())
            return buildings_schema

    async def update_building_metadata(
        self, building_id: uuid.UUID, new_metadata: dict
    ):
        """
        Update the metadata (information field) of a building.
        """
        async with self.db.session() as session:
            building = await session.get(Building, building_id)
            if building:
                building.information = new_metadata
                await session.commit()

    async def update_building(self, building_id: uuid.UUID, update: BuildingUpdate):
        """
        Update the maintenance status of a building.
        """
        async with self.db.session() as session:
            building = await session.get(Building, building_id)
            if building:
                building.requires_maintenance = update.requires_maintenance
                building.information = update.information
                building.updated_at = datetime.now()
                building.updated_by = update.updated_by
                await session.commit()

    async def delete_building(self, building_id: uuid.UUID):
        """
        Delete a building by ID.
        """
        async with self.db.session() as session:
            building = await session.get(Building, building_id)
            if building:
                await session.delete(building)
                await session.commit()

    async def get_building(
        self, building_id: uuid.UUID
    ) -> Optional[Building]:  # Return DTO
        """
        Retrieve a building by ID.
        """
        async with self.db.session() as session:
            building_orm = await session.get(
                BuildingModel, building_id
            )  # Get ORM object
            if building_orm:  # Check if the building exists
                return building_orm.as_dto()  # Convert to DTO before returning
            return None

    async def get_building_amenity(self, building_id: uuid.UUID) -> Optional[Amenity]:
        """
        Retrieve the amenity *inside* a building using PostGIS.
        """
        async with self.db.session() as session:  # Ensure async session usage
            result = await session.execute(
                select(Amenity)
                .join(Building, func.ST_Contains(Building.geometry, Amenity.geometry))
                .filter(Building.id == building_id)
            )
            return result.scalars().first()  # Get the first matching amenity

    async def get_amenities_within_radius(
        self, point: str, radius: int
    ) -> List[Amenity]:
        """
        Retrieve all amenities within a given radius of a point.
        """
        async with self.db.session() as session:
            point = func.ST_GeomFromGeoJSON(point)
            amenities = (
                await session.query(Amenity)
                .filter(func.ST_DWithin(Amenity.geometry, point, radius))
                .all()
            )

            return amenities
