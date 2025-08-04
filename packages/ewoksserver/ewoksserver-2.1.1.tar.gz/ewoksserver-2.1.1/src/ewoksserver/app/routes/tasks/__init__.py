from .router import router as _router

routers = {
    (1, 0, 0): _router,
    (1, 1, 0): _router,
    (2, 0, 0): _router,
}
