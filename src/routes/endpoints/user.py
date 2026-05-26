from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from routes.dependencies import get_current_user, get_service
from schemas.base import PaginateResponse
from schemas.user import AddPermissionCommand, AddRoleCommand, PermissionResponse, RoleResponse, UserResponse
from services.user_services import UserService
from src.routes.middlewares import DecoratorUtil

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])


@cbv(router)
class UserRouter:
    service: UserService = Depends(get_service)

    @router.get("/", response_model=PaginateResponse[UserResponse])
    @DecoratorUtil.require_access("users:read")
    def get_users(self, page: int = 1, page_size: int = 10):
        return self.service.get_users(page, page_size)

    @router.post("/role/", response_model=RoleResponse)
    def add_role(self, body: AddRoleCommand):
        return self.service.add_role(body=body)

    @router.get("/role/", response_model=PaginateResponse[RoleResponse])
    def get_roles(self, page: int = 1, page_size: int = 10):
        return self.service.get_roles(page, page_size)

    @router.post("/permission/", response_model=PermissionResponse)
    def post_permission(self, body: AddPermissionCommand):
        return self.service.add_permission(body=body)

    @router.get("/permission/", response_model=PaginateResponse[PermissionResponse])
    def get_permissions(self, page: int = 1, page_size: int = 10):
        return self.service.get_permissions(page, page_size)
