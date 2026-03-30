from fastapi import status


class AppException(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class AuthenticationException(AppException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(AppException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class ResourceNotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail, status.HTTP_409_CONFLICT)


class UserNotFoundException(ResourceNotFoundException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail)


class UserAlreadyExistsException(ConflictException):
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(detail)


class UserCreateException(AppException):
    def __init__(self, detail: str = "Unable to create user"):
        super().__init__(detail, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserUpdateException(AppException):
    def __init__(self, detail: str = "Unable to update user"):
        super().__init__(detail, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShipmentNotFoundException(ResourceNotFoundException):
    def __init__(self, detail: str = "Shipment not found"):
        super().__init__(detail)


class TrackingNotFoundException(ResourceNotFoundException):
    def __init__(self, detail: str = "Tracking record not found"):
        super().__init__(detail)


class HubNotFoundException(ResourceNotFoundException):
    def __init__(self, detail: str = "Hub not found"):
        super().__init__(detail)
