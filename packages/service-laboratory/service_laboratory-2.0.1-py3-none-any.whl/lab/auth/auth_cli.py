import os

import yaml
from faker import Faker
import click
from click import Group
from litestar.plugins import CLIPluginProtocol
from sqlalchemy import delete

from ..core.cli import coro
from ..core.database import session_maker
from .auth_core import hash_password
from .models import PermissionModel, RoleModel, UserModel, RolePermissionAssociation, UserRoleAssociation
from .repositories.permission_repository import provide_permission_repository
from .repositories.role_repository import provide_role_repository
from .repositories.user_repository import provide_user_repository


fake = Faker()

class AuthLoader:
    def __init__(self, session):
        self.session = session

    async def generate_users(self):
        password = hash_password("password")

        user_repository = await provide_user_repository(self.session)
        await user_repository.add_many(
            [UserModel(email=fake.unique.email(), password=password) for _ in range(497)],
            auto_commit=True
        )

    async def generate_data(self):
        permission_repository = await provide_permission_repository(self.session)
        role_repository = await provide_role_repository(self.session)
        user_repository = await provide_user_repository(self.session)

        await self.session.execute(delete(RolePermissionAssociation))
        await self.session.execute(delete(UserRoleAssociation))

        await permission_repository.delete_where()
        await role_repository.delete_where()
        await user_repository.delete_where()

        await permission_repository.delete_where(auto_commit=True)
        await role_repository.delete_where(auto_commit=True)
        await user_repository.delete_where(auto_commit=True)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./fixtures/auth.yaml"), "r") as stream:
            data_loaded = yaml.safe_load(stream)
            permissions = await permission_repository.add_many(
                [
                    PermissionModel(app=app, name=name)
                    for app, names in data_loaded.get("permissions").items()
                    for name in names
                ],
                auto_commit=True,
            )

            roles = []
            for name, permission_values in data_loaded.get("roles").items():
                role = RoleModel(name=name)
                role_permission_filter = {
                    app: {name for name in names}
                    for app, names in permission_values.items()
                }
                for permission in permissions:
                    if permission.name in role_permission_filter.get(permission.app):
                        role.permissions.append(permission)
                roles.append(role)

            await role_repository.add_many(roles, auto_commit=True)
            users = []

            for user_data in data_loaded.get("users"):
                email = user_data.get("email")
                users_roles = {role for role in user_data.get("roles")}

                user = UserModel(email=email, password=hash_password("password"))
                for role in roles:
                    if role.name in users_roles:
                        user.roles.append(role)
                users.append(user)
            await user_repository.add_many(users, auto_commit=True)

        click.secho("Success loaded auth data", fg="green")

        await self.generate_users()


class AuthCLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        @cli.group(help="Manage auth, load data with ``load`` command")
        @click.version_option(prog_name='mycli')
        def auth():
            ...

        @auth.command(help="Load auth initial data")
        @coro
        async def load():
            async with session_maker() as session:
                auth_loader = AuthLoader(session)
                await auth_loader.generate_data()