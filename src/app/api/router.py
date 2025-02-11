from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

api_router = APIRouter(prefix="/api")


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


@api_router.get("/amenities")
async def get_amenities(request: Request):
    return await request.app.state.service.get_amenities()


@api_router.get("/route")
async def get_route(request: Request):
    return await request.app.state.service.get_route()


def setup_static(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")
