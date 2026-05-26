from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    document_number: str


class TokenResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int
    token_type: str


@dataclass(frozen=True)
class UserCommand:
    email: str
    password: str
    full_name: str
    document_number: str


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class RefreshCommand:
    email: str
    refresh_token: str


@dataclass(frozen=True)
class AddRoleCommand:
    user_id: UUID
    role: str


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


@dataclass(frozen=True)
class AddPermissionCommand:
    role_id: UUID
    permission: str


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
