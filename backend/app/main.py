"""FastAPI backend entry point for SSHFerry."""
from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import api_router
from backend.app.config import DEFAULT_ALLOWED_ORIGINS
from backend.app.services.app_state import AppState
from src import __version__


@asynccontextmanager
async def lifespan_factory(app: FastAPI, app_state_factory: Callable[[], AppState]):
    """Initialize and clean up shared backend state."""
    app_state = app_state_factory()
    app_state.start()
    app.state.app_state = app_state
    try:
        yield
    finally:
        app_state.stop()


def create_app(app_state_factory: Callable[[], AppState] | None = None) -> FastAPI:
    """Create the FastAPI application."""
    factory = app_state_factory or AppState
    preview_state = factory()
    runtime_settings = getattr(preview_state, 'runtime_settings', None)
    allow_origins = list(getattr(runtime_settings, 'allowed_origins', DEFAULT_ALLOWED_ORIGINS))
    allow_credentials = bool(getattr(runtime_settings, 'allow_credentials', False))

    app = FastAPI(
        title='SSHFerry Backend',
        version=__version__,
        lifespan=lambda app_instance: lifespan_factory(app_instance, factory),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(api_router, prefix='/api')
    return app


app = create_app()


def run() -> None:
    """Run the backend service."""
    host = os.getenv('SSHFERRY_BACKEND_HOST', '127.0.0.1')
    port = int(os.getenv('SSHFERRY_BACKEND_PORT', '18080'))
    uvicorn.run('backend.app.main:app', host=host, port=port, reload=False)


if __name__ == '__main__':
    run()
