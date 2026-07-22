from fastapi import status


class AppException(Exception):
    """
    Unified Base Exception wrapper for the entire application.
    All custom production domain faults must inherit from this parent wrapper.
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected system execution anomaly occurred."

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code
        super().__init__(self.detail)


# CORE AUTHENTICATION DOMAIN FAULTS
class AuthenticationError(AppException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "Administrative login credentials could not be verified."


class AccountDisabledError(AppException):
    status_code: int = status.HTTP_403_FORBIDDEN
    detail: str = "This administrative workspace profile has been deactivated."


# DATA TRANSFORMATION DOMAIN FAULTS
class ContactProcessingError(AppException):
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail: str = "Provided contact data file contains malformed structures or fields."


class DuplicateContactError(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    detail: str = "This normalized phone number record already exists inside the repository."


class EntityNotFoundError(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "The requested file allocation batch or contact row was not found."
