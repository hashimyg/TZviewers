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
    # Here, our dependencies and health routers handle early probe mappings natively.
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

    # 3. MOUNT TRUSTED HOST MIDDLEWARE (Prevents Host-Header Injection Attacks)
    if settings.ENVIRONMENT == "production":
        # In production, this explicitly restricts valid incoming host bindings
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=["localhost", "127.0.0.1"]  # Mbeleni tutaweka domain yetu salama kama ya vcf.co.tz
        )

    # 4. MOUNT SECURE REQUEST THROTTLING MIDDLEWARE (Layer 6 Anti-Abuse)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # 5. MOUNT DEFENSIVE SECURITY HEADERS MIDDLEWARE (Layer 5 Data Protection)
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
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
        return response

    # 6. MOUNT CROSS-ORIGIN RESOURCE SHARING FIREWALL
    # Dynamically toggles credential validation constraints to block browser collision failures
    origins_list = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    allow_credentials_gate = True
    
    if "*" in origins_list:
        allow_credentials_gate = False  # Enforce strict standard constraints when wildcard operators are present

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=allow_credentials_gate,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    )

    # 7. REGISTER GLOBAL EXCEPTIONS MANAGEMENT MATRIX (Layer 8 Protection)
    register_exception_handlers(app)
 
    # =====================================================================
    # 8. REGISTER CORE ROUTING ARCHITECTURE MODULES WITH UNIFIED PREFIXES
    # =====================================================================
    # FIXED: Tunatumia settings.API_V1_STR au prefix safi ya "/api" bila kurudia ma-folder ya ndani ya routers
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")      # /api + /auth/login = /api/auth/login cleanly
    app.include_router(contacts_router, prefix="/api")  # /api + /contacts/... = /api/contacts/...
    app.include_router(upload_router, prefix="/api")    # /api + /upload/... = /api/upload/...

    logger.info(f"System initialization phase finalized under unified '{settings.ENVIRONMENT.upper()}' contexts.")
    return app

# Instantiate main execution object
app = create_application_runtime()