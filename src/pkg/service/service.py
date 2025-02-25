import random
from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from src.pkg.deps.interfaces import ServiceInterface, RepositoryInterface
from src.pkg.models import (
    Building,
    Amenity,
    BuildingUpdate,
    AmenityUpdate,
    ClosestAmenityResponse,
    InsightsResponse,
)
from src.pkg.adapters.terra import TerraClient
from src.pkg.adapters.overpass import OverpassClient
from src.pkg.adapters.mapbox import MapboxClient
from src.pkg.models.enums import AmenityCategory


class Service(ServiceInterface):
    def __init__(
        self,
        repository: RepositoryInterface,
        terra_client: TerraClient,
        overpass_client: OverpassClient,
        mapbox_client: MapboxClient,
        feature_collection_id: str,
        feature_id: str,
    ):
        self._repository = repository
        self._overpass_client = overpass_client
        self._terra_client = terra_client
        self._mapbox_client = mapbox_client
        self._feature_collection_id = feature_collection_id
        self._feature_id = feature_id

    async def get_building_image(self, building_id: str) -> Optional[bytes]:
        building = await self._repository.get_building(building_id)
        if not building:
            return None

        return await self._mapbox_client.get_static_image(building.as_geojson_string())

    async def sync_buildings(self) -> bool:
        success = False
        try:
            boundaries = await self._fetch_boundaries()
            buildings = await self._overpass_client.extract_buildings(boundaries)
            await self._repository.load_buildings(buildings)
            success = True
        except Exception as e:
            print(f"syncing buildings failed. Error: {e}")
        return success

    async def sync_amenities(self) -> bool:
        success = False
        try:
            boundaries = await self._fetch_boundaries()
            amenities = await self._overpass_client.extract_amenities(boundaries)
            await self._repository.load_amenities(amenities)
            success = True
        except Exception as e:
            print(f"syncing amenities failed. Error: {e}")
        return success

    async def assign_closest_amenities(self) -> bool:
        success = False
        try:
            await self._repository.assign_closest_amenities()
            success = True
        except Exception as e:
            print(f"assigning closest amenities failed. Error: {e}")
        return success

    async def get_buildings(self) -> List[Building]:
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
                information=building.information,
                requires_maintenance=building.requires_maintenance,
                updated_by=building.updated_by,
            ),
        )
        return building_amenity

    async def get_closest_amenity(
        self, building_id: str, category: str
    ) -> Optional[ClosestAmenityResponse]:
        building = await self._repository.get_building(building_id)

        amenity = await self._repository.get_closest_amenity(
            building_id, AmenityCategory(category)
        )
        if not amenity:
            return None
        route = await self._terra_client.get_route(
            [
                (
                    building.shapely_geometry.centroid.x,
                    building.shapely_geometry.centroid.y,
                ),
                (amenity.shapely_geometry.x, amenity.shapely_geometry.y),
            ]
        )
        return ClosestAmenityResponse(amenity=amenity.as_geojson_string(), route=route)

    async def _fetch_boundaries(self):
        feature = await self._terra_client.fetch_collection_feature(
            self._feature_collection_id, self._feature_id
        )
        if not feature:
            raise ValueError("Feature with boundaries not found")
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

    @staticmethod
    def get_maintenance_data(buildings: List[Building]):
        maintenance_count = defaultdict(int)

        for building in buildings:
            if building.requires_maintenance:
                month_year = building.updated_at.strftime("%b-%y")
                maintenance_count[month_year] += 1

        maintenance_list = sorted(
            [
                {
                    "month": month,
                    "count": str(count),
                    "maintained_buildings": str(max(0, count + random.randint(-4, 4))),
                }
                for month, count in maintenance_count.items()
            ],
            key=lambda x: datetime.strptime(x["month"], "%b-%y"),
        )

        maintenance_months_list = [entry["month"] for entry in maintenance_list]
        maintenance_count_list = [int(entry["count"]) for entry in maintenance_list]
        maintained_buildings_list = [
            int(entry["maintained_buildings"]) for entry in maintenance_list
        ]

        total_maintenance_requests = sum(maintenance_count_list)
        average_maintenance_count = (
            total_maintenance_requests / len(maintenance_count_list)
            if maintenance_count_list
            else 0
        )
        trending_rate = (
            round(
                (maintenance_count_list[-1] - maintenance_count_list[-2])
                / maintenance_count_list[-1]
                * 100,
                1,
            )
            if len(maintenance_list) > 1
            else 0
        )

        return {
            "maintenance_list": maintenance_list,
            "maintenance_months_list": maintenance_months_list,
            "maintenance_count_list": maintenance_count_list,
            "maintained_buildings_list": maintained_buildings_list,
            "max_value": max(
                maintenance_count_list + maintained_buildings_list, default=0
            ),
            "total_maintenance_requests": total_maintenance_requests,
            "average_maintenance_count": round(average_maintenance_count, 2),
            "trending_rate": trending_rate,
            "buildings_in_good_condition": len(buildings) - total_maintenance_requests,
        }

    @staticmethod
    def get_historic_buildings(buildings: List[Building]):
        historic_buildings = [b for b in buildings if "historic" in b.information]
        historic_buildings_requires_maintenance = [
            b for b in historic_buildings if b.requires_maintenance
        ]

        return {
            "historic_buildings": historic_buildings,
            "historic_buildings_count": len(historic_buildings),
            "historic_buildings_requires_maintenance": [
                b.model_dump(by_alias=True)
                for b in historic_buildings_requires_maintenance
            ],
            "historic_buildings_requires_maintenance_count": len(
                historic_buildings_requires_maintenance
            ),
        }

    @staticmethod
    def get_latest_buildings(buildings: List[Building], count=5) -> List[Building]:
        buildings_sorted = sorted(buildings, key=lambda x: x.updated_at, reverse=True)
        return buildings_sorted[:count]

    @staticmethod
    def get_amenity_data(amenities: List[Amenity]):
        sum_amenities = len(amenities)
        distinct_amenity_types = list(
            {a.amenity_type for a in amenities if a.amenity_type}
        )

        restaurant_count = sum(
            1
            for a in amenities
            if a.amenity_type
            and any(x in a.amenity_type.lower() for x in ["restaurant", "cafe", "wifi"])
        )
        amenity_types = [
            {
                "amenity_type": item.replace("_", " ").title(),
                "count": sum(1 for a in amenities if a.amenity_type == item),
                "percentage": round(
                    sum(1 for a in amenities if a.amenity_type == item)
                    / sum_amenities
                    * 100,
                    2,
                ),
            }
            for item in distinct_amenity_types
        ]
        amenity_types.append(
            {
                "amenity_type": "Restaurant",
                "count": restaurant_count,
                "percentage": round(restaurant_count / sum_amenities * 100, 2),
            }
        )

        distinct_amenity_categories = list({a.amenity_category for a in amenities})
        other_categories_count = sum(
            1 for a in amenities if a.amenity_category in [None, "", "Other Amenities"]
        )
        amenity_categories = [
            {
                "category": item.replace("_", " ").title(),
                "count": sum(1 for a in amenities if a.amenity_category == item),
                "percentage": round(
                    sum(1 for a in amenities if a.amenity_category == item)
                    / sum_amenities
                    * 100,
                    2,
                ),
            }
            for item in distinct_amenity_categories
            if item not in [None, "", "Other Amenities"]
        ]
        if other_categories_count > 0:
            amenity_categories.append(
                {
                    "category": "Other Amenities",
                    "count": other_categories_count,
                    "percentage": round(
                        other_categories_count / sum_amenities * 100, 2
                    ),
                }
            )

        return {
            "amenities_count": sum_amenities,
            "amenity_types": amenity_types,
            "amenity_categories": amenity_categories,
            "categories_list": [c["category"] for c in amenity_categories],
            "categories_counts_list": [c["count"] for c in amenity_categories],
            "categories_percentage_list": [c["percentage"] for c in amenity_categories],
            "background_colors": ["#efd58a", "#38a3cd", "#a8a9ab", "#9fd9f3"],
        }

    async def get_insights(self) -> InsightsResponse:
        buildings = await self.get_buildings()
        amenities = await self.get_amenities()

        data_variables = {}

        data_variables["buildings_count"] = len(buildings)
        data_variables.update(self.get_maintenance_data(buildings))
        data_variables.update(self.get_historic_buildings(buildings))
        data_variables["latest_5_buildings"] = self.get_latest_buildings(buildings)
        data_variables.update(self.get_amenity_data(amenities))

        return InsightsResponse(**data_variables)
