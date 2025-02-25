from fastapi import APIRouter, FastAPI, Request, Response
from src.pkg.models import AmenityUpdate, BuildingUpdate

api_router = APIRouter(prefix="/api")


@api_router.get("/buildings")
async def get_buildings(request: Request):
    return await request.app.state.service.get_buildings()


@api_router.get("/buildings/geojson")
async def get_buildings_geojson(request: Request):
    buildings = await request.app.state.service.get_buildings()

    return {
        "type": "FeatureCollection",
        "features": [b.as_geojson() for b in buildings],
    }


@api_router.patch("/buildings/{building_id}")
async def update_building(request: Request, building_id: str, update: BuildingUpdate):
    """Fixing the order of arguments and ensuring await is used"""
    return await request.app.state.service.update_building(building_id, update)


@api_router.delete("/buildings/{building_id}")
async def delete_building(request: Request, building_id: str):
    building = await request.app.state.service.get_building(building_id)
    if not building:
        return {"error": "Building not found."}, 404

    await request.app.state.service.delete_building(building)
    return {"message": "Building deleted."}


@api_router.get("/buildings/{building_id}/amenity")
async def get_building_amenity(request: Request, building_id: str):
    return await request.app.state.service.get_building_amenity(building_id)


@api_router.get("/buildings/{building_id}/closest/{category}")
async def get_closest_amenity(request: Request, building_id: str, category: str):
    return await request.app.state.service.get_closest_amenity(building_id, category)


@api_router.get("/buildings/{building_id}/image")
async def get_building_image(request: Request, building_id: str):
    image_bytes = await request.app.state.service.get_building_image(building_id)
    return Response(content=image_bytes, media_type="image/png")


@api_router.get("/amenities")
async def get_amenities(request: Request):
    return await request.app.state.service.get_amenities()


@api_router.get("/amenities/geojson")
async def get_amenities_geojson(request: Request):
    amenities = await request.app.state.service.get_amenities()
    return {
        "type": "FeatureCollection",
        "features": [a.as_geojson() for a in amenities],
    }


@api_router.patch("/amenities/{amenity_id}")
async def update_amenity(request: Request, amenity_id: str, update: AmenityUpdate):
    """Fixing parameter order and ensuring await is used"""
    return await request.app.state.service.update_amenity(amenity_id, update)


@api_router.delete("/amenities/{amenity_id}")
async def delete_amenity(request: Request, amenity_id: str):
    amenity = await request.app.state.service.get_amenity(amenity_id)
    if not amenity:
        return {"error": "Amenity not found."}, 404

    await request.app.state.service.delete_amenity(amenity)
    return {"message": "Amenity deleted."}
