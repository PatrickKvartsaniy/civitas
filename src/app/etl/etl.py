from src.pkg.deps.interfaces import ServiceInterface


class ETL:
    def __init__(self, config, service: ServiceInterface):
        self.config = config
        self.service = service

    async def __call__(self):
        await self.sync()

    async def sync(self):
        # await self.service.sync_buildings()
        # await self.service.sync_amenities()
        await self.service.assign_closest_amenities()
