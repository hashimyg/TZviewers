import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.base import AppException

# Set up dedicated isolated error logger for tracking anomalies securely
logger = logging.getLogger("app.exceptions")


def register_exception_handlers(app: FastAPI) -> None:
    """
    Binds global application interceptors to the live FastAPI runtime instance context.
    Safely captures custom exceptions and enforces a normalized error response model.
    """

    @app.exception_handler(AppException)
    async def unified_app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """
        Catches customized domain layer faults. Logs the internal trace metrics safely 
        behind Nginx boundaries while exposing a sanitized structural feedback block to the client.
        """
        logger.warning(
            f"Domain Exception Intercepted [{exc.status_code}]: {exc.detail} | "
            f"Path: {request.url.path} | Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.__class__.__name__,
                "message": exc.detail
            }
        )

    @app.exception_handler(Exception)
    async def global_fallback_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        The absolute Last Line of Defense. Catch-all wrapper for unexpected generic codes 
        (e.g., unexpected network drop, disk space exhaustion). Completely replaces 
        default HTML trace dumps with pure, anonymous safety payload blocks.
        """
        # Critical Alert Tracking: Records the actual raw stack trace to our hidden app.log file
        logger.critical(
            f"CRITICAL SYSTEM ERROR UNCAUGHT: {str(exc)} | "
            f"Path: {request.url.path} | Method: {request.method}", 
            exc_info=True
        )

        # FIXED SECURITY GUARD: Explicitly imported 'status' resolves the runtime NameError crash loop
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_code": "InternalServerError",
                "message": "A critical system anomaly occurred. This event signature has been securely logged."
            }
        )
