from app.main import app
from collections.abc import AsyncIterator

import pytest

from litestar import Litestar
from litestar.testing import AsyncTestClient

from ..api import AccountController
from ..api.account_controller import UserDetailResponse
from ..services import UserService
from ..auth_core import encode_jwt_token
from ..models import UserModel
from ..middleware import API_KEY_HEADER, TOKEN_PREFIX


async def test_get_users(test_client: AsyncTestClient[Litestar], user_service: UserService, users) -> None:
    admin = await user_service.repository.get_one(UserModel.email=="admin@mail.com")
    user = UserDetailResponse.model_validate(admin)
    access_token = encode_jwt_token(user.model_dump(mode="json"))
    response = await test_client.get("/api/auth/users", headers={
        "Accept": "application/json",
        API_KEY_HEADER: f"{TOKEN_PREFIX}{access_token}"
    })
    response_data = response.json()
    assert len(response_data["items"]) == 20
    assert response_data['total'] == 500


async def test_login(test_client: AsyncTestClient[Litestar], user_service: UserService, users) -> None:
    admin = await user_service.repository.get_one(UserModel.email=="admin@mail.com")

    response = await test_client.post("/api/auth/account/login", json={
        "email": admin.email,
        "password": "password",
    })

async def test_get_account(test_client: AsyncTestClient[Litestar], user_service: UserService, users) -> None:
    admin = await user_service.repository.get_one(UserModel.email=="admin@mail.com")
    access_token = AccountController.generate_token(admin)
    response = await test_client.get("/api/auth/account/me", headers={
        "Accept": "application/json",
        API_KEY_HEADER: f"{TOKEN_PREFIX}{access_token}"
    })
    response_data = response.json()
    assert response_data.get('email') == admin.email
