import uvicorn
import asyncio
import signal
import logging
from fastapi import FastAPI

from .api import api_router
from .etl import ETL
from .events import lifespan
from src.pkg.config.env import get_settings, Settings
from src.pkg.infrastructure.postgresql import DatabaseSessionManager
from src.pkg.repository.repository import Repository
from src.pkg.service.service import Service


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

    def serve(self):
        logger.info("Starting web server...")
        uvicorn.run(self._web_engine, host=self._cfg.HOST, port=self._cfg.PORT)

    async def shutdown(self):
        """Graceful shutdown handler."""
        logger.warning("Shutting down gracefully...")
        # Perform cleanup (close database, stop ETL, etc.)
        # await self._etl_engine.cleanup()
        logger.info("Shutdown complete.")


def create_app(cfg: Settings) -> App:
    """Create and configure the application."""
    db = DatabaseSessionManager(str(cfg.get_db_url()))
    repo = Repository(bounding_box=cfg.BOUNDING_BOX, db=db)
    service = Service(repo)

    etl = ETL(config=cfg, service=service)

    web = FastAPI(
        lifespan=lifespan,
        title=cfg.PROJECT_NAME,
    )
    web.state.service = service
    web.include_router(api_router)

    return App(cfg, etl, web)
