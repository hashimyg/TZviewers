from app.api.routers.auth import router as auth_router
from app.api.routers.contacts import router as contacts_router
from app.api.routers.upload import router as upload_router
from app.api.routers.health import router as health_router

__all__ = ["auth_router", "contacts_router", "upload_router", "health_router"]
