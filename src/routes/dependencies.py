from functools import lru_cache

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.envs import aws_settings
from repositiories.user_repo import UserRepo
from services.user_services import UserService
from src.core.context import permissions_var

bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    url = (
        f"https://cognito-idp.{aws_settings.DEPLOY_REGION}.amazonaws.com"
        f"/{aws_settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    )
    return requests.get(url, timeout=5).json()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:
        data = jwt.decode(
            credentials.credentials,
            _get_jwks(),
            algorithms=["RS256"],
            audience=aws_settings.COGNITO_CLIENT_ID,
        )
        email = data["username"]
        permissions = await UserService(UserRepo()).get_permissions_by_email(email=email)
        permissions_var.set(permissions)
        return data
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_service() -> UserService:
    return UserService(UserRepo())
