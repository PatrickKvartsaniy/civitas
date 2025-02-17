import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.future import select
from sqlalchemy import func, update
from sqlalchemy.orm import aliased
from sqlalchemy.util.preloaded import orm

from src.pkg.infrastructure.postgresql import DatabaseSessionManager
from src.pkg.models import (
    Amenity,
    Building,
    AmenityUpdate,
    BuildingUpdate,
    AmenityCategory,
)

from .models import (
    Amenity as AmenityModel,
    Building as BuildingModel,
)


class PersistenceRepository:
    def __init__(self, db: DatabaseSessionManager):
        self.db = db

    async def load_amenity(
        self,
        amenity: Amenity,
    ):
        """
        Insert or update an amenity into the database.
        """
        async with self.db.session() as session:
            amenity = AmenityModel(
                osm_id=amenity.osm_id,
                name=amenity.name,
                amenity_type=amenity.amenity_type,
                amenity_category=amenity.amenity_category,
                address=amenity.address,
                opening_hours=amenity.opening_hours,
                geometry=amenity.geometry,
                updated_at=amenity.updated_at,
                updated_by=amenity.updated_by,
            )
            session.add(amenity)
            await session.commit()

    async def load_amenities(self, amenities: List[Amenity]):
        """Load multiple amenities into DB."""
        if not amenities:  # Avoid unnecessary DB calls if list is empty
            return

        async with self.db.session() as session:
            async with session.begin():
                session.add_all(
                    [
                        AmenityModel(
                            osm_id=a.osm_id,
                            name=a.name,
                            amenity_type=a.amenity_type,
                            amenity_category=a.amenity_category,
                            address=a.address,
                            opening_hours=a.opening_hours,
                            geometry=a.geometry,
                            updated_at=a.updated_at,
                            updated_by=a.updated_by,
                        )
                        for a in amenities
                    ]
                )

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

    async def update_amenity(
        self, amenity_id: uuid.UUID, amenity_update: AmenityUpdate
    ):
        """
        Update the metadata (information field) of an amenity.
        """
        async with self.db.session() as session:
            amenity = await session.get(Amenity, amenity_id)
            if amenity:
                amenity.name = amenity_update.name
                amenity.amenity_type = amenity_update.amenity_type
                amenity.address = amenity_update.amenity_update
                amenity.opening_hours = amenity_update.opening_hours
                amenity.updated_at = datetime.now()
                amenity.updated_by = amenity_update.updated_by
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

    async def load_building(self, building: Building):
        """
        Insert a new building into the database.
        """
        async with self.db.session() as session:
            building = BuildingModel(
                osm_id=building.osm_id,
                information=building.information,
                geometry=building.geometry,
                requires_maintenance=building.requires_maintenance,
                updated_at=building.updated_at,
                updated_by=building.updated_by,
            )
            session.add(building)
            await session.commit()

    async def load_buildings(self, buildings: List[Building]):
        """Load multiple buildings into DB."""
        if not buildings:  # Avoid unnecessary DB calls if list is empty
            return

        async with self.db.session() as session:
            async with session.begin():  # Ensures rollback on failure
                session.add_all(
                    [
                        BuildingModel(
                            osm_id=b.osm_id,
                            information=b.information,
                            geometry=b.geometry,
                            requires_maintenance=b.requires_maintenance,
                            updated_at=b.updated_at,
                            updated_by=b.updated_by,
                        )
                        for b in buildings
                    ]
                )

    async def get_buildings(self) -> List[Building]:
        async with self.db.session() as session:
            # Query buildings with their related amenities
            result = await session.execute(
                select(BuildingModel)
                .outerjoin(AmenityModel, BuildingModel.amenity == AmenityModel.id)
                .options(
                    orm.joinedload(BuildingModel.amenity_rel)
                )  # Eager load amenity_rel
            )

            buildings_orm = result.scalars().all()
            buildings_schema = [building_orm.as_dto() for building_orm in buildings_orm]

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

    async def update_building(
        self, building_id: uuid.UUID, building_update: BuildingUpdate
    ):
        """
        Update the maintenance status of a building.
        """
        async with self.db.session() as session:
            building = await session.get(Building, building_id)
            if building:
                building.requires_maintenance = building_update.requires_maintenance
                building.information = building_update.information
                building.updated_at = datetime.now()
                building.updated_by = building_update.updated_by
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
                BuildingModel,
                building_id,
                options=[orm.joinedload(BuildingModel.amenity_rel)],  # Eager load
            )
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
                .filter(BuildingModel.id == building_id)
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

    async def assign_closest_amenities(self):
        async with self.db.session() as session:
            closest_amenity = aliased(AmenityModel)

            SEARCH_RADIUS = 2  # in meters

            # Find the closest amenity for each building
            subquery = (
                select(
                    BuildingModel.id.label("building_id"),
                    closest_amenity.id.label("amenity_id"),
                    func.ST_Distance(
                        BuildingModel.geometry, closest_amenity.geometry
                    ).label("distance"),
                    func.row_number()
                    .over(
                        partition_by=BuildingModel.id,  # Rank per building (fixing the previous issue)
                        order_by=func.ST_Distance(
                            BuildingModel.geometry, closest_amenity.geometry
                        ),
                    )
                    .label("rank"),
                )
                .join(
                    closest_amenity,
                    func.ST_DWithin(
                        BuildingModel.geometry, closest_amenity.geometry, SEARCH_RADIUS
                    ),
                )
                .subquery()
            )

            # Select only the top-ranked closest amenity per building
            ranked_amenities_cte = (
                select(subquery.c.building_id, subquery.c.amenity_id)
                .where(subquery.c.rank == 1)
                .cte("ranked_amenities")
            )

            # Update the buildings table
            update_stmt = (
                update(BuildingModel)
                .values(amenity=ranked_amenities_cte.c.amenity_id)
                .where(BuildingModel.id == ranked_amenities_cte.c.building_id)
            )

            # Execute the update
            await session.execute(update_stmt)
            await session.commit()

    async def find_closest_amenity_by_category(
        self,
        building_id: uuid.UUID,
        amenity_category: AmenityCategory,
        range_meters: int = 5000,
    ) -> Optional[Amenity]:
        """
        Find the closest amenity of a specific type to a building.
        """
        async with self.db.session() as session:
            building = await session.get(
                BuildingModel, building_id
            )  # Fetch the building
            if not building:
                return None  # Building not found

            closest_amenity = aliased(AmenityModel)  # Alias for AmenityModel

            # Query to find the closest amenity of the specified type
            result = await session.execute(
                select(closest_amenity)
                .join(
                    BuildingModel,
                    func.ST_DWithin(
                        BuildingModel.geometry, closest_amenity.geometry, range_meters
                    ),
                )
                .filter(BuildingModel.id == building_id)
                .filter(closest_amenity.amenity_category == amenity_category)
                .order_by(
                    func.ST_Distance(BuildingModel.geometry, closest_amenity.geometry)
                )  # Order by distance
            )

            amenity = result.scalars().first()
            if amenity:
                return amenity.as_dto()  # Return the DTO
            return None
