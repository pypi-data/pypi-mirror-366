import logging
from pprint import pformat

from fastapi import FastAPI

from .config import get_app_settings
from .cors import enable_cors
from .lifespan import fastapi_lifespan
from .routes import backend
from .routes import frontend
from .routes import tasks
from .routes import workflows
from .routes import icons
from .routes import execution

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create the main API instance"""
    settings = get_app_settings()

    backend.assert_route_versions(
        tasks.routers,
        workflows.routers,
        icons.routers,
        execution.routers,
        execution.app_creators,
    )
    all_routes = (
        backend.get_routes("tasks", tasks.routers),
        backend.get_routes("workflows", workflows.routers),
        backend.get_routes("icons", icons.routers),
        backend.get_routes("execution", execution.routers),
        backend.get_routes("execution", execution.app_creators, suffix="socket.io"),
    )
    version_tags = backend.extract_version_tags(all_routes)
    major, minor, patch = backend.extract_latest_version(all_routes)

    tags_metadata = [
        {"name": "tasks", "description": "Ewoks workflow tasks"},
        {"name": "workflows", "description": "Ewoks workflows"},
        {"name": "icons", "description": "Ewoks workflow icons"},
        {"name": "execution", "description": "Ewoks workflow execution"},
        *(
            {"name": tag, "description": f"Ewoks workflows API {tag}"}
            for tag in version_tags
        ),
    ]

    app = FastAPI(
        title="ewoks",
        summary="Edit and execute ewoks workflows",
        version=f"{major}.{minor}.{patch}",
        contact={
            "name": "ESRF",
            "url": "https://gitlab.esrf.fr/workflow/ewoks/ewoksserver/issues",
        },
        license_info={
            "name": "MIT",
            "identifier": "MIT",
        },
        openapi_tags=tags_metadata,
        lifespan=fastapi_lifespan,
        openapi_url="/openapi.json",
        docs_url="/docs",
        swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
        redoc_url="/redoc",
    )

    enable_cors(app)

    backend.add_routes(
        app,
        all_routes,
        no_older_versions=settings.no_older_versions,
    )

    frontend.add_frontend(app)  # Needs to come last for some reason

    logger.debug(f"Routes \n {pformat(app.routes)}")

    return app
