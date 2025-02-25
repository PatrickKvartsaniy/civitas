import os
import json
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# API Router for web pages
web_router = APIRouter(prefix="")


# Home Page
@web_router.get("/", response_class=HTMLResponse)
@web_router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "base.html", {"request": request, "title": "Home"}
    )


# Map Explorer Page
@web_router.get("/mapexplorer", response_class=HTMLResponse)
async def map_explorer(request: Request):
    return templates.TemplateResponse(
        "MapExplorer.html", {"request": request, "title": "Map Explorer"}
    )


# Full-Screen Map Page
@web_router.get("/map", response_class=HTMLResponse)
async def map_page(request: Request):
    return templates.TemplateResponse("map.html", {"request": request, "title": "Map"})


# Dashboard Page
@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    context = {
        "request": request,
        "title": "Dashboard",
        "data_variables": request.app.state.service.data_variables,  # Assuming this exists
    }
    return templates.TemplateResponse("Dashboard.html", context)


# Insights Dashboard Page
@web_router.get("/dashboard/index", response_class=HTMLResponse)
async def dashboard_index(request: Request):
    context = {
        "request": request,
        "title": "Insights Dashboard",
        "today_date": datetime.today().strftime("%b %d, %Y"),  # Example: Feb 13, 2025
        "current_hour": datetime.now().strftime("%H") + ":00",
        "data_variables": request.app.state.service.data_variables,  # Assuming this exists
    }
    return templates.TemplateResponse("dashboard_index.html", context)


# 3D Viewer Page
@web_router.get("/threedviewer", response_class=HTMLResponse)
async def threed_viewer(request: Request):
    return templates.TemplateResponse(
        "ThreeDViewer.html", {"request": request, "title": "3D Viewer"}
    )


# 🗺️ Map Amenities Page
@web_router.get("/map/amenities", response_class=HTMLResponse)
async def map_amenities_page(request: Request):
    buildings = await request.app.state.service.get_buildings()

    feature_collection = {
        "type": "FeatureCollection",
        "features": [b.as_geojson() for b in buildings],
    }

    return templates.TemplateResponse(
        "map/amenities.html",
        {
            "request": request,
            "mapbox_access_token": request.app.state.cfg.MAPBOX_ACCESS_TOKEN,
            "api_url": request.app.state.cfg.API_URL,
            "buildings": json.dumps(feature_collection),
        },
    )


# 🏗️ Map Maintenance Page
@web_router.get("/map/maintenance", response_class=HTMLResponse)
async def map_maintenance_page(request: Request):
    buildings = await request.app.state.service.get_buildings()

    feature_collection = {
        "type": "FeatureCollection",
        "features": [b.as_geojson() for b in buildings],
    }

    return templates.TemplateResponse(
        "map/maintenance.html",
        {
            "request": request,
            "mapbox_access_token": request.app.state.cfg.MAPBOX_ACCESS_TOKEN,
            "api_url": request.app.state.cfg.API_URL,
            "buildings": json.dumps(feature_collection),
        },
    )
