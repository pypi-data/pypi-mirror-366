from typing import List
from uuid import UUID

import advanced_alchemy
from litestar import Request, get, post
from litestar.connection import ASGIConnection
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.handlers.base import BaseRouteHandler
from pydantic import BaseModel, ConfigDict, SecretStr

from ..auth_core import check_password, encode_jwt_token
from ..models import UserModel
from ..repositories import UserRepository, provide_user_repository


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Role(Base):
    id: UUID | None
    name: str


class UserDetailResponse(Base):
    id: UUID | None
    email: str
    password: SecretStr
    roles: List[Role]


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: UserDetailResponse


def admin_user_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    if connection.user.get("role") != "admin":
        raise NotAuthorizedException()


class AccountController(Controller):
    @staticmethod
    def generate_token(user_data: UserModel) -> str:
        user = UserDetailResponse.model_validate(user_data)
        return encode_jwt_token(user.model_dump(mode="json"))

    dependencies = {
        "user_repository": Provide(provide_user_repository),
    }
    path = "/account"

    @post(
        path="/login",
        exclude_from_auth=True,
    )
    async def login(
            self,
            user_repository: UserRepository,
            data: LoginRequest,
    ) -> LoginResponse:
        try:
            admin = await user_repository.get_one(UserModel.email == data.email)
        except advanced_alchemy.exceptions.NotFoundError:
            raise NotFoundException(f"User with email {data.email} not found")

        if not check_password(
            data.password,
            admin.password,
        ):
            raise NotFoundException("Invalid password")

        access_token = self.generate_token(admin)

        return LoginResponse(
            user=UserDetailResponse.model_validate(admin),
            access_token=access_token,
        )

    @get(path="/me")
    async def me(self, request: Request) -> UserDetailResponse:
        if not request.user:
            raise NotAuthorizedException()

        return UserDetailResponse(**request.user)
