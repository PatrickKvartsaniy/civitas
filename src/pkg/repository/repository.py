import logging
from typing import List

from src.pkg.deps.interfaces import RepositoryInterface
from src.pkg.models import Amenity, Building, AdminBoundary
from src.pkg.repository.persistence.queries import PersistenceRepository

logger = logging.getLogger(__name__)


class Repository(RepositoryInterface):
    def __init__(self, db):
        super().__init__()
        self._persistence_repo = PersistenceRepository(db)

    async def get_amenities(self) -> List[Amenity]:
        return await self._persistence_repo.get_amenities()

    async def get_buildings(self) -> List[Building]:
        return await self._persistence_repo.get_buildings()

    async def update_amenity(self, amenity: Amenity):
        await self._persistence_repo.update_name(amenity.id, amenity.name)

    async def update_building(self, building: Building):
        await self._persistence_repo.update_metadata(building.id, building.metadata)

    async def load_amenities(self, amenities: List[Amenity]):
        logger.info(f"Loading {len(amenities)} amenities...")
        for amenity in amenities:
            await self._persistence_repo.load_amenity(
                amenity.osm_id,
                amenity.name,
                amenity.amenity_type,
                amenity.address,
                amenity.opening_hours,
                amenity.geometry,
                amenity.updated_at,
                amenity.updated_by,
            )

    async def load_buildings(self, buildings: List[Building]):
        logger.info(f"Loading {len(buildings)} buildings...")
        for building in buildings:
            await self._persistence_repo.load_building(
                building.osm_id, building.information, building.geometry
            )
