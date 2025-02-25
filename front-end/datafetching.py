from datetime import datetime
import uuid
from collections import Counter
from collections import defaultdict
import json
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import random

########################## Mock ##########################
# mock data to be used in case of any server error

buildings_sample_list = [
    {
        "id": "ba06f016-d6f7-48c1-b53f-015e07e1a0e8",
        "osm_id": 400755438,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.485536 35.8904152, 14.4855802 35.8900712, 14.4854741 35.8900783, 14.485536 35.8904152))",
        "height": 11,
        "requires_maintenance": "true",
        "amenity": {
            "id": "f39a1724-680f-4938-ba45-1caf43a8187c",
            "osm_id": 2523304904,
            "name": "Cosmed",
            "amenity_type": "pharmacy",
            "amenity_category": "Other Amenities",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.4860315 35.8906842)",
            "updated_at": "2025-02-19T17:43:06.656235",
            "updated_by": None,
        },
        "updated_at": "2025-02-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "041ad67e-c1ec-417a-9bc7-fe532210cd5c",
        "osm_id": 395232860,
        "information": {
            "building": "yes",
            "historic": "building",
            "name": "Bieb Hompesch",
        },
        "geometry": "POLYGON ((14.5271448 35.8721042, 14.5271381 35.8720527, 14.5271316 35.8720031, 14.5270881 35.8720069, 14.5270946 35.8720565, 14.5271013 35.8721079, 14.5271448 35.8721042))",
        "height": 6,
        "requires_maintenance": "true",
        "amenity": {
            "id": "604260a7-65c7-4835-b01d-6850c0eb4492",
            "osm_id": 5129977526,
            "name": "Hompesch",
            "amenity_type": "pharmacy",
            "amenity_category": "Other Amenities",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5259101 35.8722372)",
            "updated_at": "2025-02-19T17:43:06.669173",
            "updated_by": None,
        },
        "updated_at": "2025-02-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "ba06f016-d6f7-48c1-b53f-015e07e1a0e8",
        "osm_id": 400755438,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.485536 35.8904152, 14.4855802 35.8900712, 14.4854741 35.8900783, 14.485536 35.8904152))",
        "height": 11,
        "requires_maintenance": "true",
        "amenity": {
            "id": "f39a1724-680f-4938-ba45-1caf43a8187c",
            "osm_id": 2523304904,
            "name": "Cosmed",
            "amenity_type": "pharmacy",
            "amenity_category": "Other Amenities",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.4860315 35.8906842)",
            "updated_at": "2025-02-19T17:43:06.656235",
            "updated_by": None,
        },
        "updated_at": "2025-02-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "44c163b8-8c0e-4f24-9499-9603ca2ed182",
        "osm_id": 1356217846,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.509865 35.8376396, 14.5099091 35.8375688, 14.5100597 35.8376305, 14.5100156 35.8377013, 14.509865 35.8376396))",
        "height": 7,
        "requires_maintenance": "true",
        "amenity": {
            "id": "644a3e4b-a0fb-4623-be17-c1fc25a3dd2c",
            "osm_id": 5119365581,
            "name": "It-Turretta",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5142407 35.8474939)",
            "updated_at": "2025-02-19T17:43:06.669086",
            "updated_by": None,
        },
        "updated_at": "2025-02-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "00035ffb-d144-4a32-8755-3e2ef3618ae4",
        "osm_id": 394928421,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.4162554 35.9166879, 14.416343 35.9166456, 14.4163421 35.9166191, 14.416374 35.9166005, 14.4164147 35.9166134, 14.41645 35.916594, 14.4164562 35.9165625, 14.4164961 35.9165446, 14.4164049 35.9164184, 14.4162917 35.9164708, 14.4162961 35.9164994, 14.4162483 35.9165216, 14.4162023 35.9165116, 14.4161775 35.9165317, 14.4161935 35.9165575, 14.4161687 35.9165768, 14.416189 35.9166005, 14.4161758 35.9166169, 14.4161926 35.9166363, 14.4161926 35.9166506, 14.4162173 35.9166793, 14.4162554 35.9166879))",
        "height": 12,
        "requires_maintenance": "false",
        "amenity": {
            "id": "5549a4fe-babe-48be-b8f0-7f9b71381e43",
            "osm_id": 5160347299,
            "name": "Premiere car sales",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.4182978 35.9164672)",
            "updated_at": "2025-02-19T17:43:06.669539",
            "updated_by": None,
        },
        "updated_at": "2024-10-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "44c163b8-8c0e-4f24-9499-9603ca2ed182",
        "osm_id": 1356217846,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.509865 35.8376396, 14.5099091 35.8375688, 14.5100597 35.8376305, 14.5100156 35.8377013, 14.509865 35.8376396))",
        "height": 7,
        "requires_maintenance": "true",
        "amenity": {
            "id": "644a3e4b-a0fb-4623-be17-c1fc25a3dd2c",
            "osm_id": 5119365581,
            "name": "It-Turretta",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5142407 35.8474939)",
            "updated_at": "2025-02-19T17:43:06.669086",
            "updated_by": None,
        },
        "updated_at": "2025-01-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "44c163b8-8c0e-4f24-9499-9603ca2ed182",
        "osm_id": 1356217846,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.509865 35.8376396, 14.5099091 35.8375688, 14.5100597 35.8376305, 14.5100156 35.8377013, 14.509865 35.8376396))",
        "height": 7,
        "requires_maintenance": "true",
        "amenity": {
            "id": "644a3e4b-a0fb-4623-be17-c1fc25a3dd2c",
            "osm_id": 5119365581,
            "name": "It-Turretta",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5142407 35.8474939)",
            "updated_at": "2025-02-19T17:43:06.669086",
            "updated_by": None,
        },
        "updated_at": "2024-09-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "44c163b8-8c0e-4f24-9499-9603ca2ed182",
        "osm_id": 1356217846,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.509865 35.8376396, 14.5099091 35.8375688, 14.5100597 35.8376305, 14.5100156 35.8377013, 14.509865 35.8376396))",
        "height": 7,
        "requires_maintenance": "true",
        "amenity": {
            "id": "644a3e4b-a0fb-4623-be17-c1fc25a3dd2c",
            "osm_id": 5119365581,
            "name": "It-Turretta",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5142407 35.8474939)",
            "updated_at": "2025-02-19T17:43:06.669086",
            "updated_by": None,
        },
        "updated_at": "2024-09-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "44c163b8-8c0e-4f24-9499-9603ca2ed182",
        "osm_id": 1356217846,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.509865 35.8376396, 14.5099091 35.8375688, 14.5100597 35.8376305, 14.5100156 35.8377013, 14.509865 35.8376396))",
        "height": 7,
        "requires_maintenance": "true",
        "amenity": {
            "id": "644a3e4b-a0fb-4623-be17-c1fc25a3dd2c",
            "osm_id": 5119365581,
            "name": "It-Turretta",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5142407 35.8474939)",
            "updated_at": "2025-02-19T17:43:06.669086",
            "updated_by": None,
        },
        "updated_at": "2024-12-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "44c163b8-8c0e-4f24-9499-9603ca2ed182",
        "osm_id": 1356217846,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.509865 35.8376396, 14.5099091 35.8375688, 14.5100597 35.8376305, 14.5100156 35.8377013, 14.509865 35.8376396))",
        "height": 7,
        "requires_maintenance": "true",
        "amenity": {
            "id": "644a3e4b-a0fb-4623-be17-c1fc25a3dd2c",
            "osm_id": 5119365581,
            "name": "It-Turretta",
            "amenity_type": None,
            "amenity_category": "",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.5142407 35.8474939)",
            "updated_at": "2025-02-19T17:43:06.669086",
            "updated_by": None,
        },
        "updated_at": "2025-01-19T17:43:08.189345",
        "updated_by": None,
    },
    {
        "id": "0038a30b-37d6-4eb0-8010-19fd22056c56",
        "osm_id": 527722800,
        "information": {
            "addr:city": "Iż-Żejtun",
            "addr:country": "MT",
            "addr:postcode": "ŻTN 3000",
            "building": "industrial",
        },
        "geometry": "POLYGON ((14.5261778 35.8644096, 14.5266468 35.8644202, 14.5266482 35.8644865, 14.5267005 35.8644876, 14.5266609 35.8640296, 14.5266581 35.863656, 14.5262805 35.8636515, 14.5261828 35.8637268, 14.5261778 35.8644096))",
        "height": 4,
        "requires_maintenance": "false",
        "amenity": {
            "id": "5ce0303c-22ab-4bee-baa0-fb4eb124bb24",
            "osm_id": 1061670097,
            "name": None,
            "amenity_type": None,
            "amenity_category": "Residential",
            "address": None,
            "opening_hours": None,
            "geometry": "POINT (14.523085 35.868524)",
            "updated_at": "2023-12-08T23:09:11.729495",
            "updated_by": None,
        },
        "amenity_category": "Residential",
        "updated_at": "2023-12-27T20:32:45.115804",
        "updated_by": None,
    },
    {
        "id": "003c0c66-25e3-46ab-a98b-7662d8d5fcc8",
        "osm_id": 329675651,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.4753268 35.8739354, 14.4753268 35.873692, 14.4755859 35.8737033, 14.4754958 35.8739637, 14.4753268 35.8739354))",
        "height": 5,
        "requires_maintenance": "true",
        "amenity": {
            "id": "64a30f01-5c17-435e-aa88-0df3ad974e1d",
            "osm_id": 8409071980,
            "name": "M. A. Motorcycles Ltd.",
            "amenity_type": None,
            "amenity_category": "Residential",
            "address": None,
            "opening_hours": "Mo-Fr 09:00-18:00; Sa 09:00-13:00; PH closed",
            "geometry": "POINT (14.4750986 35.8753925)",
            "updated_at": "2024-01-28T05:50:05.150681",
            "updated_by": None,
        },
        "amenity_category": "Residential",
        "updated_at": "2024-01-24T10:54:21.780790",
        "updated_by": None,
    },
    {
        "id": "003e6b59-e8ae-4929-a4e5-b2c1969f4840",
        "osm_id": 367747565,
        "information": {"building": "yes"},
        "geometry": "POLYGON ((14.407668 35.8815791, 14.4077349 35.8815417, 14.4076707 35.8814704, 14.4076921 35.8814552, 14.4076707 35.8814269, 14.4075661 35.8814878, 14.4076089 35.8815438, 14.4076412 35.8815182, 14.407668 35.8815791))",
        "height": 8,
        "requires_maintenance": "false",
        "amenity": {
            "id": "14b2ce1b-26ec-4796-bec3-7874cd5cab3c",
            "osm_id": 5270463847,
            "name": "The Fork and Cork Restaurant",
            "amenity_type": "restaurant",
            "amenity_category": "Food and Drink",
            "address": "Telgħa tas-Saqqajja",
            "opening_hours": "Mo, We 12:00-14:30, 17:30-21:30; Th-Sa 17:30-21:30",
            "geometry": "POINT (14.4039043 35.8831431)",
            "updated_at": "2023-12-29T17:02:27.696526",
            "updated_by": None,
        },
        "amenity_category": "Food and Drink",
        "updated_at": "2023-12-30T08:15:08.576529",
        "updated_by": None,
    },
]


#################### Fetch the data from your API####################
# Fetch the data from your API
buildings_response = requests.get("https://civitas-471b.onrender.com/api/buildings")
if buildings_response.status_code == 200:
    buildings = buildings_response.json()
    print(
        f"Successfully fetched the data of the building"
    )  # for be sure that amenities are fetched
    # Check if there are buildings in the response
    if isinstance(buildings, list) and len(buildings) > 0:
        column_names = buildings[0].keys()  # Get keys from the first building record
        print("Column names:", list(column_names))
    else:
        print("No building data available.")
else:
    print(f"Failed to fetch data buildings: {buildings_response.status_code}")
    buildings = buildings_sample_list


# Fetch the data from your API
amenities_response = requests.get("https://civitas-471b.onrender.com/api/amenities")
if amenities_response.status_code == 200:
    amenities = amenities_response.json()
    # print(amenities[1]['amenity_type']) # for testing
    # for be sure that amenities are fetched
    print(f"Successfully fetched the data of the amenities")
else:
    print(f"Failed to fetch data amenities: {amenities_response.status_code}")
    # mock data for any server error
    amenities = [
        {
            "id": str(uuid.uuid4()),
            "osm_id": 12345,
            "name": "Mock Restaurant 1",
            "amenity_type": "restaurant",
            "amenity_category": "Food and Drink",
            "address": "123 Mock St",
            "opening_hours": "9:00-21:00",
            "geometry": {
                "type": "Point",
                "coordinates": [10.0, 20.0],
            },
            "updated_at": "2025-01-19T17:43:08.189345",
            "updated_by": "mock_user",
        },
        {
            "id": str(uuid.uuid4()),
            "osm_id": 67890,
            "name": "Mock Cafe 1",
            "amenity_type": "cafe",
            "amenity_category": "Food and Drink",
            "address": "456 Mock Ave",
            "opening_hours": "7:00-18:00",
            "geometry": {
                "type": "Point",
                "coordinates": [15.0, 25.0],
            },
            "updated_at": "2025-01-19T17:43:08.189345",
            "updated_by": "mock_user",
        },
        {
            "id": str(uuid.uuid4()),
            "osm_id": 13579,
            "name": "Mock Bank 1",
            "amenity_type": "bank",
            "amenity_category": "Commercial and Financial",
            "address": "789 Mock Blvd",
            "opening_hours": "10:00-16:00",
            "geometry": {
                "type": "Point",
                "coordinates": [20.0, 30.0],
            },
            "updated_at": "2025-01-19T17:43:08.189345",
            "updated_by": "mock_user",
        },
        {
            "id": str(uuid.uuid4()),
            "osm_id": 24680,
            "name": "Mock Park 1",
            "amenity_type": "park",  # Example without a direct category mapping
            "address": "101 Mock Cr",
            "opening_hours": "Always Open",
            "geometry": {
                "type": "Point",
                "coordinates": [25.0, 35.0],
            },
            "updated_at": "2025-01-19T17:43:08.189345",
            "updated_by": "mock_user",
        },
        {
            "id": str(uuid.uuid4()),
            "osm_id": 36912,
            "name": "Mock School 1",
            "amenity_type": "school",
            "amenity_category": "Community and Culture",
            "address": "222 Mock Rd",
            "opening_hours": "8:00-15:00",
            "geometry": {
                "type": "Point",
                "coordinates": [30.0, 40.0],
            },
            "updated_at": "2025-01-19T17:43:08.189345",
            "updated_by": "mock_user",
        },
    ]
