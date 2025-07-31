import pytest
from typing import Dict

from ..auth_cli import AuthLoader
from ..services import UserService
from ..models import UserModel
from ..api import AccountController
from ..middleware import API_KEY_HEADER, TOKEN_PREFIX


@pytest.fixture(scope="session")
async def users(db_session):
    auth_loader = AuthLoader(db_session)
    await auth_loader.generate_data()


@pytest.fixture()
async def user_service(db_session) -> UserService:
    return UserService(db_session)


@pytest.fixture()
async def admin_headers(users, user_service: UserService) -> Dict[str, str]:
    admin = await user_service.repository.get_one(UserModel.email=="admin@mail.com")
    access_token = AccountController.generate_token(admin)
    return {
        "Accept": "application/json",
        API_KEY_HEADER: f"{TOKEN_PREFIX}{access_token}"
    }