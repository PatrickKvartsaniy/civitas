import os
from functools import wraps

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from starlette.middleware.sessions import SessionMiddleware


def setup_static(app: FastAPI):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Function for enabling CORS on web server
def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key="VERY_SECRET_KEY",
    )


def requires_login(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        name = request.session.get("name")
        if not name:
            return RedirectResponse(
                request.url_for("login"), status_code=status.HTTP_302_FOUND
            )
        return await func(request, *args, **kwargs)  # Call the original function

    return wrapper
