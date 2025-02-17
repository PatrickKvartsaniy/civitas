from abc import ABC, abstractmethod

from typing import List

from src.pkg.models import (
    Amenity,
    Building,
    BuildingUpdate,
    AmenityUpdate,
    ClosestAmenityResponse,
)
from src.pkg.models.literals import AmenityCategory


class RepositoryInterface(ABC):
    @abstractmethod
    async def load_amenities(self, amenities: List[Amenity]):
        raise NotImplementedError

    @abstractmethod
    async def load_buildings(self, buildings: List[Building]):
        raise NotImplementedError

    @abstractmethod
    async def get_amenities(self) -> List[Amenity]:
        raise NotImplementedError

    @abstractmethod
    async def get_buildings(self) -> List[Building]:
        raise NotImplementedError

    @abstractmethod
    async def update_building(self, building_id: str, update: BuildingUpdate):
        raise NotImplementedError

    @abstractmethod
    async def update_amenity(self, amenity_id: str, update: AmenityUpdate):
        raise NotImplementedError

    @abstractmethod
    async def get_building_amenity(self, building_id: str) -> Amenity:
        raise NotImplementedError

    @abstractmethod
    async def get_building(self, building_id: str) -> Building:
        raise NotImplementedError

    @abstractmethod
    async def assign_closest_amenities(self):
        raise NotImplementedError

    @abstractmethod
    async def get_closest_amenity(
        self, building_id: str, category: AmenityCategory
    ) -> Amenity:
        raise NotImplementedError


class ServiceInterface(ABC):
    @abstractmethod
    async def sync_buildings(self):
        raise NotImplementedError

    @abstractmethod
    async def sync_amenities(self):
        raise NotImplementedError

    @abstractmethod
    async def assign_closest_amenities(self):
        raise NotImplementedError

    @abstractmethod
    async def get_buildings(self) -> List[Building]:
        raise NotImplementedError

    @abstractmethod
    async def get_amenities(self) -> List[Amenity]:
        raise NotImplementedError

    @abstractmethod
    async def get_building_amenity(self, building_id: str) -> Amenity:
        raise NotImplementedError

    @abstractmethod
    async def get_closest_amenity(
        self, building_id: str, category: str
    ) -> ClosestAmenityResponse:
        raise NotImplementedError
