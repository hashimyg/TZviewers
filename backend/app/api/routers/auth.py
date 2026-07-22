import logging
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

# FIXED BOUNDARY IMPORT: Point strictly to the dedicated dependencies layer context
from app.dependencies.database import get_db
from app.schemas.auth import AdminLogin, Token
from app.services.auth_service import AuthService

logger = logging.getLogger("app.api.auth")

# 1. INSTANTIATE ISOLATED AUTHENTICATION ROUTER UNIT
router = APIRouter(prefix="/auth", tags=["Administrative Authentication"])


@router.post(
    "/login", 
    response_model=Token, 
    status_code=status.HTTP_200_OK,
    summary="Authenticates administrative login credentials and provisions secure JWT sessions."
)
async def login_admin_for_access_token(
    login_data: AdminLogin, 
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Core administrative session provisioning gateway.
    Interceptors scan user parameters through verified firewalls before executing cryptographic evaluation.
    """
    logger.info(f"Processing incoming administrative validation cycle query for target identifier: '{login_data.username}'")
    
    # Delegate tracking execution directly to our hardened business logic layer
    token_payload = await AuthService.authenticate_admin(login_data=login_data, db=db)
    
    logger.info(f"Administrative session successfully established for context profile: '{login_data.username}'")
    return token_payload


@router.post(
    "/login-form",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    include_in_schema=True,
    summary="OAuth2-compliant form-data login gateway for automated tools (e.g., Swagger interactive UI Docs)."
)
async def login_admin_via_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Alternative administrative entry checkpoint.
    Standardizes application workflows with standard OAuth2 password request specs 
    to enable interactive documentation testing interfaces inside FastAPI seamlessly.
    """
    logger.info(f"Form-data access authentication intercept fired for descriptor context: '{form_data.username}'")
    
    # Restructure incoming string matrices into our validated schema frame to guarantee data parity matches
    login_schema = AdminLogin(
        username=form_data.username,
        password=form_data.password
    )
    
    # Process transaction parameters symmetrically through the primary validation sequence
    token_payload = await AuthService.authenticate_admin(login_data=login_schema, db=db)
    return token_payload
