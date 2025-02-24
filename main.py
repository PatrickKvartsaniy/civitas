import argparse
import asyncio
import logging
import sys

from src.app import create_app
from src.pkg.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=settings.LOG_LEVEL,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the desired app.")
    parser.add_argument(
        "app",
        choices=["web", "etl"],
        help="The app to run: 'web' for the web app, 'etl' for the ETL app.",
    )
    parser.add_argument(
        "--automigrate",
        action="store_true",
        help="Run Alembic migrations before starting the app",
    )
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    app = create_app(settings)

    if args.app == "web":
        logger.info("Starting the web app...")
        app.serve()
    elif args.app == "etl":
        asyncio.run(app.sync())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Shutdown requested. Exiting...")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
