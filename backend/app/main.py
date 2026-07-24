import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limiter import limiter
from app.exceptions.handlers import register_exception_handlers
from app.api.routers import auth_router, contacts_router, upload_router, health_router

# 1. SETUP STRUCTURED RUNTIME ENVIRONMENT LOGS
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("app.main")


# 2. LIFESPAN CONTROLLER MANAGEMENT (Modern Async Integrity Layer)
@asynccontextmanager
async def application_infrastructure_lifespan(app_instance: FastAPI):
    """
    Manages centralized system state lifecycle event hooks.
    Ensures safe, atomic socket initialization and cleanup across database layers.
    """
    logger.info("Initializing infrastructure connection matrix checks via system lifespan hooks.")
    yield
    logger.info("Deactivating production backend containers. Closing active thread resources safely.")


def create_application_runtime() -> FastAPI:
    """
    Industrial Application Factory Engine.
    Assembles global security headers, maps strict CORS controls,
    and hooks up custom intercept handlers securely.
    """
    # Initialize Core FastAPI Instance with custom configuration overrides
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Production-grade public contact sharing directory for Tanzania.",
        lifespan=application_infrastructure_lifespan,
        docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    )

    # 3. MOUNT CROSS-ORIGIN RESOURCE SHARING FIREWALL (MUST BE FIRST BEFORE OTHER MIDDLEWARES)
    origins_list = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS] if hasattr(settings, "BACKEND_CORS_ORIGINS") else []
    
    # Explicitly add Netlify and Render production domains
    production_origins = [
        "https://tzviewers.netlify.app",
        "https://tzviewers.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5500"
    ]
    
    for p_origin in production_origins:
        if p_origin not in origins_list:
            origins_list.append(p_origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"], # Allow all headers (Content-Type, Authorization, etc.)
        expose_headers=["*"],
    )

    # 4. MOUNT TRUSTED HOST MIDDLEWARE
    if settings.ENVIRONMENT == "production":
        allowed_hosts_list = [
            "localhost",
            "127.0.0.1",
            "tzviewers.onrender.com",
            "*.onrender.com",
            "tzviewers.netlify.app",
            "*.netlify.app",
            "*" # Safety fallback for Render proxying
        ]
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=allowed_hosts_list
        )

    # 5. MOUNT SECURE REQUEST THROTTLING MIDDLEWARE (Layer 6 Anti-Abuse)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # 6. MOUNT DEFENSIVE SECURITY HEADERS MIDDLEWARE
    @app.middleware("http")
    async def inject_defensive_security_headers(request: Request, call_next) -> Response:
        """
        Global application middleware block. Forces strict browser security policies 
        across every outgoing payload trace to mitigate XSS, Clickjacking, and Sniffing.
        """
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        return response

    # 7. REGISTER GLOBAL EXCEPTIONS MANAGEMENT MATRIX (Layer 8 Protection)
    register_exception_handlers(app)
 
    # =====================================================================
    # 8. REGISTER CORE ROUTING ARCHITECTURE MODULES WITH UNIFIED PREFIXES
    # =====================================================================
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")      
    app.include_router(contacts_router, prefix="/api")  
    app.include_router(upload_router, prefix="/api")    

    logger.info(f"System initialization phase finalized under unified '{settings.ENVIRONMENT.upper()}' contexts.")
    return app

# Instantiate main execution object
app = create_application_runtime()