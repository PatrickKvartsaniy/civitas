import os
import json
from datetime import datetime

from fastapi import APIRouter, Request, status
from fastapi.params import Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .router import requires_login

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# API Router for web pages
web_router = APIRouter(prefix="")


@web_router.get("/", response_class=HTMLResponse)
@web_router.get("/home", response_class=HTMLResponse)
@requires_login
async def home(request: Request):
    name = request.session.get("name")
    return templates.TemplateResponse(
        "base.html", {"request": request, "title": "Home", "username": name}
    )


@web_router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "Login"}
    )


@web_router.post("/login")
async def login_submit(request: Request, name: str = Form(...)):
    request.session["name"] = name
    return RedirectResponse(
        request.url_for("home"), status_code=status.HTTP_303_SEE_OTHER
    )  # Use 303 for POST redirects


@web_router.get("/logout")
async def logout(request: Request):
    request.session.clear()  # Clear the session
    return RedirectResponse(request.url_for("login"))


@requires_login
@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    name = request.session.get("name")

    context = {
        "request": request,
        "title": "Dashboard",
        "username": name,
    }
    return templates.TemplateResponse("Dashboard.html", context)


@requires_login
@web_router.get("/dashboard/index", response_class=HTMLResponse)
async def dashboard_index(request: Request):
    data_variables = await request.app.state.service.get_insights()
    name = request.session.get("name")

    context = {
        "request": request,
        "title": "Insights Dashboard",
        "today_date": datetime.today().strftime("%b %d, %Y"),
        "current_hour": datetime.now().strftime("%H") + ":00",
        "data_variables": data_variables,
        "username": name,
    }
    return templates.TemplateResponse("Dashboard_index.html", context)


@requires_login
@web_router.get("/map/amenities", response_class=HTMLResponse)
async def map_amenities_page(request: Request):
    buildings = await request.app.state.service.get_buildings()
    name = request.session.get("name")

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
            "username": name,
        },
    )


@requires_login
@web_router.get("/map/maintenance", response_class=HTMLResponse)
async def map_maintenance_page(request: Request):
    buildings = await request.app.state.service.get_buildings()
    name = request.session.get("name")

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
            "username": name,
        },
    )
