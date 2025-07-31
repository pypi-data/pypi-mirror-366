from sqlalchemy.ext.asyncio.session import AsyncSession
from ..models import UserModel


async def test_create_user(db_session: AsyncSession, user_service):
    user_data = UserModel(
        email="some3@email.com",
        password="super_password",
    )
    user_data = await user_service.create(user_data, auto_commit=True)
    user = await user_service.get(user_data.id)
    assert user.email == user_data.email
    await user_service.delete(user_data.id)



async def test_get_users(db_session, users, user_service):
    users = await user_service.list()
    assert len(users) == 500


