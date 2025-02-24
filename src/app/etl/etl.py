import logging

from src.pkg.deps.interfaces import ServiceInterface

logger = logging.getLogger(__name__)


class ETL:
    def __init__(self, config, service: ServiceInterface):
        self.config = config
        self.service = service

    async def __call__(self):
        await self.sync()

    async def sync(self):
        logger.info("Starting the ETL process...")
        await self._run_sync()
        logger.info("ETL process completed.")

    async def _run_sync(self):
        if not await self.service.sync_buildings():  # <1>
            logger.error("Failed to sync buildings. Exiting...")
            return
        if not await self.service.sync_amenities():  # <2>
            logger.error("Failed to sync amenities. Exiting...")
            return
        if not await self.service.assign_closest_amenities():  # <3>
            logger.error("Failed to assign closest amenities. Exiting...")
            return
