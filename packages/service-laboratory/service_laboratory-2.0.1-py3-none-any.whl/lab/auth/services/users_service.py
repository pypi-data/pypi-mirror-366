from __future__ import annotations

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from ..models import UserModel

__all__ = ("UserService",)


class UserService(SQLAlchemyAsyncRepositoryService[UserModel]):
    class Repository(SQLAlchemyAsyncRepository[UserModel]):
        model_type = UserModel

    repository_type = Repository
    match_fields = ["email"]
