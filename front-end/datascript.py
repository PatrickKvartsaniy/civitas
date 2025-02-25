from datetime import datetime
import uuid
from collections import Counter
import json
import requests
import uuid
from datetime import datetime
import requests
from collections import defaultdict
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import random
from datafetching import buildings, amenities

# This variable stores all necessary data to be shared across different code files
data_variables = {}

################################### Buildings ###################################

# 1-serial chart for counts of maintenance request/ response

# 2-menu of the latest maintained buildings (sorting desc)

# 3-menu of the latest requests (sorting ascending)


# it's needed to have a list for requires_maintenance (yes) and updated_at(date)
# Dictionary to store count of buildings requiring maintenance per month-year

# Dictionary to store count of buildings requiring maintenance per month-year
maintenance_count = defaultdict(int)

# Process each building
for building in buildings:
    if building["requires_maintenance"]:
        # Convert updated_at to month-year format "MMM-YY"
        date_obj = datetime.fromisoformat(building["updated_at"])
        month_year = date_obj.strftime("%b-%y")  # Example: "Feb-25"

        # Increment count for this month-year
        maintenance_count[month_year] += 1

# Convert to required list of dictionaries format with a new "maintained_buildings" key
maintenance_list = []
for month, count in maintenance_count.items():
    # making a random field for maintanence- for visualization
    # additional database edits can be done in future phases
    maintained_buildings = max(
        0, count + random.randint(-4, 4)
    )  # Ensure non-negative values
    maintenance_list.append(
        {
            "month": month,
            "count": str(count),
            "maintained_buildings": str(maintained_buildings),
        }
    )

# Sort the list based on date order
maintenance_list = sorted(
    maintenance_list, key=lambda x: datetime.strptime(x["month"], "%b-%y")
)
# print("maintenance_list")
# print(maintenance_list)

# Get the historic buildings
historic_buildings = []
historic_buildings_requires_maintenance = []
for building in buildings:
    # Check if "historic" is in any key or value (including nested dictionaries)
    if any(
        "historic" in str(key).lower() or "historic" in str(value).lower()
        for key, value in building.items()
    ):
        historic_buildings.append(building)
        if building.get("requires_maintenance") == "true":
            historic_buildings_requires_maintenance.append(building)
    else:
        # Check nested dictionaries (like "information" and "amenity")
        for key, value in building.items():
            if isinstance(value, dict):
                if any(
                    "historic" in str(k).lower() or "historic" in str(v).lower()
                    for k, v in value.items()
                ):
                    historic_buildings.append(building)
                    break  # Stop checking once we find "historic"

# Extract ordered lists
maintenance_months_list = [entry["month"] for entry in maintenance_list]
maintenance_count_list = [entry["count"] for entry in maintenance_list]
maintained_buildings_list = [
    entry["maintained_buildings"] for entry in maintenance_list
]
# print("maintained_buildings_list")
# print(maintained_buildings_list)

max_value = max(
    max(maintenance_count_list, default=0), max(maintained_buildings_list, default=0)
)
total_maintenance_requests = sum(int(x) for x in maintenance_count_list)
average_maintenance_count = total_maintenance_requests / len(maintenance_count_list)
trending_rate = round(
    (int(maintenance_list[-1]["count"]) - int(maintenance_list[-2]["count"]))
    / int(maintenance_list[-1]["count"])
    * 100,
    1,
)
historic_buildings_count = sum(1 for building in buildings if "historic" in building)
buildings_in_good_condition = len(buildings) - total_maintenance_requests

# Sort buildings by 'updated_at' in descending order
buildings_sorted = sorted(
    buildings, key=lambda x: datetime.fromisoformat(x["updated_at"]), reverse=True
)

# Get the latest 5 buildings and update 'updated_at' to only include the date
latest_5_buildings = [
    {**b, "updated_at": datetime.fromisoformat(b["updated_at"]).date().isoformat()}
    for b in buildings_sorted[:5]
]
# passing these variables to js of the dashboard
data_variables.update(
    {
        "Buildings_count": len(buildings),
        "maintenance_list": maintenance_list,
        "maintenance_months_list": maintenance_months_list,
        "maintenance_count_list": maintenance_count_list,
        "maintained_buildings_list": maintained_buildings_list,
        "max_value": max_value,
        "total_maintenance_requests": total_maintenance_requests,
        "average_maintenance_count": round(average_maintenance_count, 2),
        "trending_rate": trending_rate,
        "historic_buildings": historic_buildings,
        "historic_buildings_count": len(historic_buildings),
        "buildings_in_good_condition": buildings_in_good_condition,
        "historic_buildings_requires_maintenance": historic_buildings_requires_maintenance,
        "historic_buildings_requires_maintenance_count": len(
            historic_buildings_requires_maintenance
        ),
        "latest_5_buildings": latest_5_buildings,
    }
)
################################### Amenities ###################################

# amenities
# 1- Pie chart --> amenities types (showing counts/percentages of each type)

# Extract distinct values for "amenity_type"
distinct_amenity_types = list({amenity["amenity_type"] for amenity in amenities})

# Getting the sum of all amenities
sum_amenities = len(amenities)

# Getting the count of each type
amenity_types = []
restaurant_count = 0  # To accumulate "restaurant" counts

for item in distinct_amenity_types:
    # Count occurrences
    c = sum(1 for itemm in amenities if itemm["amenity_type"] == item)

    # If the item is related to a restaurant, add to restaurant_count
    if (
        "restaurant" in str(item).lower()
        or "cafe" in str(item).lower()
        or "wifi" in str(item).lower()
    ):
        restaurant_count += c
    elif item == None:
        # Append non-restaurant categories directly
        amenity_types.append(
            {
                "amenity_type": item,
                "count": c,
                "percentage": round(c / sum_amenities * 100, 2),
            }
        )

    else:
        # Append non-restaurant/ not categories directly
        amenity_types.append(
            {
                "amenity_type": item.replace("_", " ").title(),
                "count": c,
                "percentage": round(c / sum_amenities * 100, 2),
            }
        )

# Append "restaurants"
amenity_types.append(
    {
        "amenity_type": "Restaurant",
        "count": restaurant_count,
        "percentage": round(restaurant_count / sum_amenities * 100, 2),
    }
)

# Print the final results
# print(f"amenity_types: {amenity_types}")


# 2- bar chart for categories

# getting the values of categories
distinct_amenity_categories = list(
    {amenity["amenity_category"] for amenity in amenities}
)

# Getting the count of each category
amenity_categories = []
other_categories_count = 0  # To accumulate "Other Amenities" counts

for item in distinct_amenity_categories:
    c = 0
    for itemm in amenities:
        if item == itemm["amenity_category"]:
            c += 1  # Increment count when match is found
    if (
        item is None or item == "" or item == "Other Amenities"
    ):  # Merge categories (None/unknown/Other Amenities)
        other_categories_count += c  # Accumulate count for "Other Amenities"
    else:
        amenity_categories.append(
            {
                "category": item.replace("_", " ").title(),
                "count": c,
                "percentage": round(c / sum_amenities * 100, 2),
            }
        )

# Append "Other Amenities" if there are any (None/unknown/Other Amenities) counts
if other_categories_count > 0:
    amenity_categories.append(
        {
            "category": "Other Amenities",
            "count": other_categories_count,
            "percentage": round(other_categories_count / sum_amenities * 100, 2),
        }
    )

background_colors = ["#efd58a", "#38a3cd", "#a8a9ab", "#9fd9f3"]


# passing these variables to js of the dashboard
data_variables.update(
    {
        "amenities_count": len(amenities),
        "amenity_types": amenity_types,
        "amenity_categories": amenity_categories,
        "categories_list": [item["category"] for item in amenity_categories],
        "categories_counts_list": [item["count"] for item in amenity_categories],
        "categories_percentage_list": [
            item["percentage"] for item in amenity_categories
        ],
        "background_colors": ["#efd58a", "#38a3cd", "#a8a9ab", "#9fd9f3"],
    }
)

# results
# print(f"categories:{amenity_categories}")
# print(f"categories list: {[item["category"] for item in amenity_categories]}")
# print(f"categories precentage: {[item["percentage"] for item in amenity_categories]}")
