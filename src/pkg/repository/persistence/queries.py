import json
import uuid
from datetime import datetime
from typing import Optional, List

from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sqlalchemy.future import select

from src.pkg.infrastructure.postgresql import DatabaseSessionManager
from src.pkg.models.models import AdminBoundary, Amenity, Building

from .models import AdminBoundary as AdminBoundaryModel, Amenity as AmenityModel, Building as BuildingModel


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

    async def delete_building(self, building_id: uuid.UUID):
        """
        Delete a building by ID.
        """
        async with self.db.session() as session:
            building = await session.get(Building, building_id)
            if building:
                await session.delete(building)
                await session.commit()

    async def get_admin_boundaries(self) -> List[AdminBoundary]:
        """
        Retrieve all administrative boundaries.
        """
        async with self.db.session() as session:
            result = await session.execute(select(AdminBoundaryModel))
            amenities_orm = result.scalars().all()

            amenities_schema = []
            for amenity_orm in amenities_orm:
                amenities_schema.append(amenity_orm.as_dto())
            return amenities_schema
