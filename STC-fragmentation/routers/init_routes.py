from .websocket_routes import router as ws_router
from .pages import router as pages_router
from routers.fragment_routes import router as fragment_router
from routers.subtitle_routes import router as subtitle_router
def init_routes(app):
    app.include_router(ws_router)
    app.include_router(pages_router)
    app.include_router(fragment_router)
    app.include_router(subtitle_router)

