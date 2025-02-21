import logging
import os
import time
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.pkg.models import AmenityUpdate, BuildingUpdate

api_router = APIRouter(prefix="/api")
web_router = APIRouter(prefix="/web")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

logger = logging.getLogger(__name__)


def setup_static(app: FastAPI):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Function for enabling CORS on web server
def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@api_router.get("/buildings")
async def get_buildings(request: Request):
    return await request.app.state.service.get_buildings()


@api_router.get("/buildings/geojson")
async def get_buildings_geojson(request: Request):
    start_time_total = time.time()  # Start timing the entire function

    start_time_db = time.time()  # Start timing database query
    buildings = await request.app.state.service.get_buildings()
    end_time_db = time.time()  # End timing database query
    db_time = end_time_db - start_time_db

    start_time_geojson = time.time()  # Start timing GeoJSON conversion
    features = [b.as_geojson() for b in buildings]
    end_time_geojson = time.time()  # End timing GeoJSON conversion
    geojson_time = end_time_geojson - start_time_geojson

    geojson_response = {
        "type": "FeatureCollection",
        "features": features,
    }

    end_time_total = time.time()  # End timing the entire function
    total_time = end_time_total - start_time_total

    # Log the timings (or use a more structured logging approach)
    logger.info(f"Database Query Time: {db_time:.4f} seconds")
    logger.info(f"GeoJSON Conversion Time: {geojson_time:.4f} seconds")
    logger.info(f"Total Request Time: {total_time:.4f} seconds")

    return geojson_response


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


@web_router.get("/map/amenities", response_class=HTMLResponse)
async def map_page(request: Request):
    return templates.TemplateResponse(
        "map/amenities.html",
        {
            "request": request,
            "mapbox_access_token": request.app.state.cfg.MAPBOX_ACCESS_TOKEN,
            "api_url": request.app.state.cfg.API_URL,
        },
    )


@web_router.get("/map/maintenance", response_class=HTMLResponse)
async def maintenance_page(request: Request):
    return templates.TemplateResponse(
        "map/maintenance.html",
        {
            "request": request,
            "mapbox_access_token": request.app.state.cfg.MAPBOX_ACCESS_TOKEN,
            "api_url": request.app.state.cfg.API_URL,
        },
    )
