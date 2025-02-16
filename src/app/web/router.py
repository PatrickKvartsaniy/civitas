import os

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

api_router = APIRouter(prefix="/api")
web_router = APIRouter(prefix="/web")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# function for enabling CORS on web server
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
    buildings = await request.app.state.service.get_buildings()
    return {
        "type": "FeatureCollection",
        "features": [b.to_geojson() for b in buildings],
    }


@api_router.get("/amenities")
async def get_amenities(request: Request):
    return await request.app.state.service.get_amenities()


@api_router.get("/amenities/geojson")
async def get_amenities_geojson(request: Request):
    amenities = await request.app.state.service.get_amenities()
    return {
        "type": "FeatureCollection",
        "features": [a.to_geojson() for a in amenities],
    }


@api_router.get("/route")
async def get_route(request: Request):
    return await request.app.state.service.get_route()


@web_router.get("/map", response_class=HTMLResponse)
async def map_page(request: Request):
    return templates.TemplateResponse(
        "map/map.html",
        {
            "request": request,
            "mapbox_access_token": request.app.state.cfg.MAPBOX_ACCESS_TOKEN,
        },
    )


@web_router.get("/buildings", response_class=HTMLResponse)
async def buildings_page(request: Request):
    return templates.TemplateResponse(
        "map/buildings.html",
        {
            "request": request,
            "mapbox_access_token": request.app.state.cfg.MAPBOX_ACCESS_TOKEN,
        },
    )


def setup_static(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")
