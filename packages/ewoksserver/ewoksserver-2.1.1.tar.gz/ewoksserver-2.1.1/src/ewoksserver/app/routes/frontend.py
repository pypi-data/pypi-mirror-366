import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope

try:
    from ewoksweb.serverutils import get_static_root
except ImportError:
    get_static_root = None

from . import FRONTEND_PREFIX


logger = logging.getLogger(__name__)


class _StaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        """This gets called for every path that is not mounted or route that is not included."""
        if path in ("edit", "monitor"):
            path = ""
        return await super().get_response(path, scope)


def add_frontend(app: FastAPI) -> None:
    if get_static_root is None:
        logger.info("No frontend available to serve (pip install ewoksweb)")
    else:
        files = _StaticFiles(directory=get_static_root(), html=True)
        app.mount(f"{FRONTEND_PREFIX}", app=files, name="ewoksweb")
