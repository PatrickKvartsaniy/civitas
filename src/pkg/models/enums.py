from enum import Enum
from typing import Dict


class AmenityCategory(str, Enum):
    EMERGENCY_AND_PUBLIC_SERVICES = "Emergency and Public Services"
    COMMERCIAL_AND_FINANCIAL = "Commercial and Financial"
    FOOD_AND_DRINK = "Food and Drink"
    COMMUNITY_AND_CULTURE = "Community and Culture"
    OTHER_AMENITIES = "Other Amenities"


amenity_category_map: Dict[str, AmenityCategory] = {
    "animal_shelter": "Emergency and Public Services",
    "bank": "Commercial and Financial",
    "bar": "Food and Drink",
    "cafe": "Food and Drink",
    "car_wash": "Commercial and Financial",
    "casino": "Commercial and Financial",
    "childcare": "Community and Culture",
    "clinic": "Other Amenities",
    "coast_radar_station": "Emergency and Public Services",
    "community_centre": "Community and Culture",
    "concert_hall": "Community and Culture",
    "conference_centre": "Community and Culture",
    "courthouse": "Community and Culture",
    "events_venue": "Community and Culture",
    "fast_food": "Food and Drink",
    "feeding_place": "Other Amenities",
    "fire_station": "Emergency and Public Services",
    "food_court": "Food and Drink",
    "fuel": "Food and Drink",
    "hospital": "Emergency and Public Services",
    "library": "Community and Culture",
    "monastery": "Community and Culture",
    "parking": "Other Amenities",
    "pharmacy": "Other Amenities",
    "place_of_worship": "Community and Culture",
    "planetarium": "Community and Culture",
    "police": "Emergency and Public Services",
    "post_office": "Emergency and Public Services",
    "prison": "Emergency and Public Services",
    "pub": "Food and Drink",
    "public_building": "Emergency and Public Services",
    "recycling": "Other Amenities",
    "restaurant": "Food and Drink",
    "retirement_home": "Other Amenities",
    "school": "Community and Culture",
    "shelter": "Other Amenities",
    "social_facility": "Community and Culture",
    "stock_exchange": "Commercial and Financial",
    "studio": "Other Amenities",
    "theatre": "Community and Culture",
    "toilets": "Other Amenities",
    "townhall": "Emergency and Public Services",
    "university": "Community and Culture",
}
