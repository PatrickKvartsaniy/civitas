from typing import Callable

from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class _TerraSettings(BaseSettings):
    API_URL: str = "https://terra-b9c1fd2b2e2b.herokuapp.com/api/v0/"
    CLIENT_ID: str = "9c44f341-032f-4a6a-9ba6-e4fc2a45f617"
    CLIENT_SECRET: str = (
        "NTMxNDdjZGU1OTU3MGViNzdlMDk2Y2U1Mjg3MjZjNWI4MDQ5MGNiNDA3NmM5NjdkYTYzODI1OTk3YzRiMmNkYw=="
    )
    AREA_BOUNDARIES_COLLECTION_ID: str = "41e65f3c-2f79-4442-a3ca-741810ef4163"
    AREA_BOUNDARIES_FEATURE_ID: str = "e67c1720-e322-11ef-a667-31686f2e2bd0"


class _DatabaseSettings(BaseSettings):
    DATABASE_PG_URL: PostgresDsn = (
        "postgresql://neondb_owner:npg_jrUpozuT7g0y@ep-black-sky-a2vsl2a2-pooler.eu-central-1.aws.neon.tech/neondb"
    )

    def get_db_url(self) -> str:
        """Return database URL with asyncpg for async SQLAlchemy."""
        return str(self.DATABASE_PG_URL).replace(
            "postgresql://", "postgresql+asyncpg://"
        )


class _WebSettings(BaseSettings):
    MAPBOX_ACCESS_TOKEN: str = (
        "pk.eyJ1IjoicGV0cm8ta3ZhcnRzaWFueWkiLCJhIjoiY202ejdiMmlkMDI1ODJwc2s4NTIxeWc4dSJ9.-k0IrJNRzERdc-Qgsl_ovA"
    )


class Settings(BaseSettings):
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: str = "DEBUG"
    PROJECT_NAME: str = "Civitas"
    WEB: _WebSettings = _WebSettings()
    TERRA: _TerraSettings = _TerraSettings()
    DB: _DatabaseSettings = _DatabaseSettings()


def _configure_initial_settings() -> Callable[[], Settings]:
    load_dotenv()
    settings = Settings()

    def fn() -> Settings:
        return settings

    return fn


get_settings = _configure_initial_settings()
