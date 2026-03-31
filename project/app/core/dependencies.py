from typing import Callable, Dict

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.exceptions.custom_exceptions import AuthenticationException, AuthorizationException
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid authentication token")

    user = UserRepository().get_user_by_id(user_id)
    if not user or not user.get("is_active", True):
        raise AuthenticationException("User not found or inactive")
    return user


def require_role(*roles: str) -> Callable:
    def role_dependency(current_user: Dict = Depends(get_current_user)) -> Dict:
        if current_user.get("role") not in roles:
            raise AuthorizationException()
        return current_user

    return role_dependency


get_customer_user = require_role("customer")
get_agent_user = require_role("agent")
get_admin_user = require_role("admin")

