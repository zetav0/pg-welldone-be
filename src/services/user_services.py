import base64
import hashlib
import hmac
from typing import List

import boto3
from django.db import transaction

from core.envs import aws_settings
from repositiories.user_repo import UserRepo
from schemas.base import PaginateResponse
from schemas.user import (
    AddPermissionCommand,
    AddRoleCommand,
    LoginCommand,
    PermissionResponse,
    RefreshCommand,
    RoleResponse,
    TokenResponse,
    UserCommand,
    UserResponse,
)


class UserService:
    user_repo: UserRepo

    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo
        self.cognito_client = boto3.client(
            "cognito-idp",
            region_name=aws_settings.DEPLOY_REGION,
        )

    def get_secret_hash(self, username):
        # A keyed-hash message authentication code (HMAC) calculated using
        # the secret key of a user pool client and username plus the client
        # ID in the message.
        message = username + aws_settings.COGNITO_CLIENT_ID
        dig = hmac.new(
            aws_settings.COGNITO_CLIENT_SECRET.encode("UTF-8"), msg=message.encode("UTF-8"), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    def get_users(self, page: int, page_size: int) -> PaginateResponse[UserResponse]:
        items, count, total_pages = self.user_repo.get_users(page, page_size)
        return PaginateResponse(
            count=count,
            total_pages=total_pages,
            current_page=page,
            items=[UserResponse.model_validate(u) for u in items],
        )

    async def get_permissions_by_email(self, email: str) -> List[str]:
        permissions = await self.user_repo.get_permissions_by_email(email=email)
        if not permissions:
            return []
        return [p.name for p in permissions]

    @transaction.atomic
    def add_user(self, user: UserCommand) -> UserResponse:
        created = self.user_repo.add_user(user)
        return UserResponse.model_validate(created)

    def register_user(self, user: UserCommand) -> UserResponse:
        # create in cognito
        self.cognito_client.sign_up(
            ClientId=aws_settings.COGNITO_CLIENT_ID,
            SecretHash=self.get_secret_hash(user.email),
            Username=user.email,
            Password=user.password,
            UserAttributes=[
                {"Name": "email", "Value": user.email},
                {"Name": "name", "Value": user.full_name},
            ],
        )
        self.cognito_client.admin_confirm_sign_up(
            UserPoolId=aws_settings.COGNITO_USER_POOL_ID,
            Username=user.email,
        )
        return self.add_user(user)

    def login_user(self, credentials: LoginCommand) -> TokenResponse:
        response = self.cognito_client.admin_initiate_auth(
            UserPoolId=aws_settings.COGNITO_USER_POOL_ID,
            ClientId=aws_settings.COGNITO_CLIENT_ID,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": credentials.email,
                "PASSWORD": credentials.password,
                "SECRET_HASH": self.get_secret_hash(credentials.email),
            },
        )
        auth = response["AuthenticationResult"]
        return TokenResponse(
            access_token=auth["AccessToken"],
            id_token=auth["IdToken"],
            refresh_token=auth["RefreshToken"],
            expires_in=auth["ExpiresIn"],
            token_type=auth["TokenType"],
        )

    def refresh_token(self, body: RefreshCommand) -> TokenResponse:
        response = self.cognito_client.admin_initiate_auth(
            UserPoolId=aws_settings.COGNITO_USER_POOL_ID,
            ClientId=aws_settings.COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": body.refresh_token,
                "SECRET_HASH": self.get_secret_hash(body.email),
            },
        )
        auth = response["AuthenticationResult"]
        return TokenResponse(
            access_token=auth["AccessToken"],
            id_token=auth.get("IdToken", ""),
            refresh_token=body.refresh_token,
            expires_in=auth["ExpiresIn"],
            token_type=auth["TokenType"],
        )

    @transaction.atomic
    def add_role(self, body: AddRoleCommand) -> RoleResponse:
        user = self.user_repo.get_user_by_id(user_id=body.user_id)
        if not user:
            raise ValueError("User not found")
        return self.user_repo.add_role(body=body)

    def get_roles(self, page: int, page_size: int) -> PaginateResponse[RoleResponse]:
        items, count, total_pages = self.user_repo.get_roles(page=page, page_size=page_size)
        return PaginateResponse(
            count=count,
            total_pages=total_pages,
            current_page=page,
            items=[RoleResponse.model_validate(item) for item in items],
        )

    @transaction.atomic
    def add_permission(self, body: AddPermissionCommand) -> PermissionResponse:
        role = self.user_repo.get_role_by_id(role_id=body.role_id)
        if not role:
            raise ValueError("Role not found")
        return self.user_repo.add_permission(body=body)

    def get_permissions(self, page: int, page_size: int) -> PaginateResponse[PermissionResponse]:
        items, count, total_pages = self.user_repo.get_permissions(page=page, page_size=page_size)
        return PaginateResponse(
            count=count,
            total_pages=total_pages,
            current_page=page,
            items=[PermissionResponse.model_validate(item) for item in items],
        )
