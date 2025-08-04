from .router import v1_0_0_router as _v1_0_0_router
from .router import v1_1_0_router as _v1_1_0_router
from .router import v2_0_0_router as _v2_0_0_router
from .socketio import create_socketio_app as _create_socketio_app

routers = {
    (1, 0, 0): _v1_0_0_router,
    (1, 1, 0): _v1_1_0_router,
    (2, 0, 0): _v2_0_0_router,
}

app_creators = {
    (1, 0, 0): _create_socketio_app,
    (1, 1, 0): _create_socketio_app,
    (2, 0, 0): _create_socketio_app,
}
