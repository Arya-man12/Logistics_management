import pytest
from unittest.mock import Mock, patch

from app.exceptions.custom_exceptions import AuthenticationException, UserAlreadyExistsException
from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


def test_register_creates_user_and_returns_token():
    repository = Mock()
    repository.get_user_by_email.return_value = None
    repository.create_user.return_value = {
        "id": "user-1",
        "email": "new@example.com",
        "name": "New User",
        "role": "customer",
        "phone": "9999999999",
        "address": "123 Main St",
        "hashed_password": "salt$hash",
        "is_active": True,
        "created_at": "2026-03-30T00:00:00Z",
        "updated_at": "2026-03-30T00:00:00Z",
    }

    payload = RegisterRequest(
        name="New User",
        email="new@example.com",
        password="password123",
        role="customer",
    )

    with patch("app.services.auth_service.create_access_token", return_value="test-token"):
        service = AuthService(repository=repository)
        result = service.register(payload)

    assert result["access_token"] == "test-token"
    assert result["token_type"] == "bearer"
    assert result["user"]["email"] == "new@example.com"
    assert "hashed_password" not in result["user"]
    repository.get_user_by_email.assert_called_once_with("new@example.com")
    repository.create_user.assert_called_once()


def test_login_raises_invalid_credentials():
    repository = Mock()
    repository.get_user_by_email.return_value = None

    service = AuthService(repository=repository)
    payload = LoginRequest(email="missing@example.com", password="password123")

    with pytest.raises(AuthenticationException):
        service.login(payload)


