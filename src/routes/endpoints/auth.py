from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from routes.dependencies import get_service
from schemas.user import LoginCommand, RefreshCommand, TokenResponse, UserCommand, UserResponse
from services.user_services import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@cbv(router)
class AuthRouter:
    service: UserService = Depends(get_service)

    @router.post("/register/", response_model=UserResponse)
    def register_user(self, user: UserCommand):
        return self.service.register_user(user)

    @router.post("/login/", response_model=TokenResponse)
    def login_user(self, credentials: LoginCommand):
        return self.service.login_user(credentials)

    @router.post("/refresh/", response_model=TokenResponse)
    def refresh_token(self, body: RefreshCommand):
        return self.service.refresh_token(body)
