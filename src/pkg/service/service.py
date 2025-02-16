from typing import List

from src.pkg.deps.interfaces import ServiceInterface, RepositoryInterface
from src.pkg.models import Building, Amenity, BuildingUpdate, AmenityUpdate
from src.pkg.adapters.terra import TerraClient
from src.pkg.adapters.overpass import OverpassClient


class Service(ServiceInterface):
    def __init__(
        self,
        repository: RepositoryInterface,
        terra_client: TerraClient,
        overpass_client: OverpassClient,
        feature_collection_id: str,
        feature_id: str,
    ):
        self._repository = repository
        self._overpass_client = overpass_client
        self._terra_client = terra_client
        self._feature_collection_id = feature_collection_id
        self._feature_id = feature_id

    async def sync_buildings(self):
        try:
            boundaries = await self._fetch_boundaries()
            buildings = await self._overpass_client.extract_buildings(boundaries)
            await self._repository.load_buildings(buildings)
        except Exception as e:
            print(f"syncing buildings failed. Error: {e}")

    async def sync_amenities(self):
        try:
            boundaries = await self._fetch_boundaries()
            amenities = await self._overpass_client.extract_amenities(boundaries)
            await self._repository.load_amenities(amenities)
        except Exception as e:
            print(f"syncing amenities failed. Error: {e}")

    async def assign_closest_amenities(self):
        try:
            await self._repository.assign_closest_amenities()
        except Exception as e:
            print(f"assigning closest amenities failed. Error: {e}")

    async def get_buildings(self) -> List[Building]:
        await self._fetch_boundaries()
        return await self._repository.get_buildings()

    async def get_amenities(self) -> List[Amenity]:
        return await self._repository.get_amenities()

    async def update_building(self, building_id: str, update: BuildingUpdate):
        await self._repository.update_building(building_id, update)

    async def update_amenity(self, amenity_id: str, update: AmenityUpdate):
        await self._repository.update_amenity(amenity_id, update)

    async def get_building_amenity(self, building_id: str) -> Amenity:
        building = await self._repository.get_building(building_id)
        if building.amenity:
            return building.amenity

        building_amenity = await self._repository.get_building_amenity(building_id)
        await self._repository.update_building(
            building_id,
            BuildingUpdate(
                amenity_id=building_amenity.id,
                information=building.information,
                requires_maintenance=building.requires_maintenance,
                updated_by=building.updated_by,
            ),
        )
        return building_amenity

    async def _fetch_boundaries(self):
        feature = await self._terra_client.fetch_collection_feature(
            self._feature_collection_id, self._feature_id
        )

        # Extract geometry
        geometry = feature.get("geometry", {})
        if not geometry:
            raise ValueError("Feature has no geometry data")

        # Extract coordinates
        coordinates = geometry.get("coordinates", [])

        # Flatten nested lists and collect all (lon, lat) points
        all_coords = []

        def extract_coords(coords):
            if isinstance(coords[0], list):
                for sub_coords in coords:
                    extract_coords(sub_coords)
            else:
                all_coords.append(coords)

        extract_coords(coordinates)

        if not all_coords:
            raise ValueError("No valid coordinates found in feature")

        # Compute bounding box (min/max longitude and latitude)
        min_lon = min(coord[0] for coord in all_coords)
        min_lat = min(coord[1] for coord in all_coords)
        max_lon = max(coord[0] for coord in all_coords)
        max_lat = max(coord[1] for coord in all_coords)

        bbox = (min_lat, min_lon, max_lat, max_lon)
        return bbox
