from typing import List
from uuid import UUID

from django.core.paginator import Paginator

from models.user import Permission, Role, User
from schemas.user import AddPermissionCommand, AddRoleCommand, PermissionResponse, RoleResponse, UserCommand


class UserRepo:
    def get_users(self, page: int, page_size: int) -> tuple[list[User], int, int]:
        qs = User.objects.order_by("-updated_at")
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)
        return list(page_obj.object_list), paginator.count, paginator.num_pages

    def get_user_by_id(self, user_id: UUID) -> User:
        return User.objects.get(id=user_id)

    def add_user(self, user: UserCommand) -> User:
        return User.objects.create(
            email=user.email,
            full_name=user.full_name,
            document_number=user.document_number,
            is_active=True,
        )

    def add_role(self, body: AddRoleCommand) -> RoleResponse:
        role = Role.objects.create(user_id=body.user_id, name=body.role)
        return RoleResponse.model_validate(role)

    def get_roles(self, page: int, page_size: int) -> tuple[list[Role], int, int]:
        qs = Role.objects.order_by("-updated_at")
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)
        return list(page_obj.object_list), paginator.count, paginator.num_pages

    def get_role_by_id(self, role_id: UUID) -> Role:
        return Role.objects.get(id=role_id)

    def add_permission(self, body: AddPermissionCommand) -> PermissionResponse:
        permission = Permission.objects.create(name=body.permission, role_id=body.role_id)
        return PermissionResponse.model_validate(permission)

    def get_permissions(self, page: int, page_size: int) -> tuple[list[Permission], int, int]:
        qs = Permission.objects.order_by("-updated_at")
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)
        return list(page_obj.object_list), paginator.count, paginator.num_pages

    async def get_permissions_by_email(self, email: str) -> List[Permission]:
        return [p async for p in Permission.objects.filter(role__user__email=email)]
