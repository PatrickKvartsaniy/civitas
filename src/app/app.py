import socket

import uvicorn
import asyncio
import logging
from fastapi import FastAPI

from .web import api_router, web_router, setup_middleware, setup_static
from .etl import ETL
from .events import lifespan
from src.pkg.config.env import Settings
from src.pkg.infrastructure.postgresql import DatabaseSessionManager
from src.pkg.repository import Repository
from src.pkg.service import Service
from src.pkg.adapters.overpass import OverpassClient
from src.pkg.adapters.terra import TerraClient
from src.pkg.adapters.mapbox import MapboxClient

logger = logging.getLogger(__name__)


class App:
    def __init__(self, cfg: Settings, etl: ETL, web: FastAPI):
        self._web_engine = web
        self._etl_engine = etl
        self._cfg = cfg
        self._shutdown_event = asyncio.Event()  # Used for graceful shutdown

    async def sync(self):
        """Run ETL process."""
        return await self._etl_engine.sync()

    def serve(self, use_local_network: bool = False):
        logger.info("Starting web server...")
        host = self.get_local_ip() if use_local_network else self._cfg.HOST
        uvicorn.run(self._web_engine, host=host, port=self._cfg.PORT)

    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception as e:
            print(f"Error getting IP: {e}")
            return None

    async def shutdown(self):
        """Graceful shutdown handler."""
        logger.warning("Shutting down gracefully...")
        # Perform cleanup (close database, stop ETL, etc.)
        # await self._etl_engine.cleanup()
        logger.info("Shutdown complete.")


def create_app(cfg: Settings) -> App:
    """Create and configure the application."""
    db = DatabaseSessionManager(cfg.DB.get_db_url())
    overpass = OverpassClient()
    terra = TerraClient(
        cfg.TERRA.API_URL,
        cfg.TERRA.CLIENT_ID,
        cfg.TERRA.CLIENT_SECRET,
    )
    mapbox = MapboxClient(cfg.WEB.MAPBOX_ACCESS_TOKEN)
    repo = Repository(db)
    service = Service(
        repo,
        terra,
        overpass,
        mapbox,
        cfg.TERRA.AREA_BOUNDARIES_COLLECTION_ID,
        cfg.TERRA.AREA_BOUNDARIES_FEATURE_ID,
    )
    etl = ETL(config=cfg, service=service)

    web = FastAPI(
        lifespan=lifespan,
        title=cfg.PROJECT_NAME,
    )
    web.state.service = service
    web.state.cfg = cfg.WEB

    setup_middleware(web)
    setup_static(web)

    web.include_router(api_router)
    web.include_router(web_router)

    return App(cfg, etl, web)
