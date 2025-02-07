from typing import List

from src.pkg.deps.interfaces import ServiceInterface, RepositoryInterface
from src.pkg.repository.persistence.models import Building, Amenity
from src.pkg.adapters.terra import TerraClient
from src.pkg.adapters.overpass import OverpassClient


class Service(ServiceInterface):
    def __init__(
        self,
        repository: RepositoryInterface,
        terra_client: TerraClient,
        overpass_client: OverpassClient,
    ):
        self._repository = repository
        self._overpass_client = overpass_client
        self._terra_client = terra_client

    async def sync_buildings(self):
        try:
            boundaries = await self._terra_client.fetch_boundaries()
            buildings = await self._overpass_client.extract_buildings(boundaries)
            await self._repository.load_buildings(buildings)
        except Exception as e:
            print(f"syncing buildings failed. Error: {e}")

    async def sync_amenities(self):
        try:
            boundaries = await self._terra_client.fetch_boundaries()
            amenities = await self._overpass_client.extract_amenities(boundaries)
            await self._repository.load_amenities(amenities)
        except Exception as e:
            print(f"syncing amenities failed. Error: {e}")

    async def get_buildings(self) -> List[Building]:
        return await self._repository.get_buildings()

    async def get_amenities(self) -> List[Amenity]:
        return await self._repository.get_amenities()

    async def update_building(self, building: Building):
        await self._repository.update_building(building)

    async def update_amenity(self, amenity: Amenity):
        await self._repository.update_amenity(amenity)
