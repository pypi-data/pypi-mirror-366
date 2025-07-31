from __future__ import annotations

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from ..models import RoleModel

__all__ = ("RoleService",)


class RoleService(SQLAlchemyAsyncRepositoryService[RoleModel]):
    class Repository(SQLAlchemyAsyncRepository[RoleModel]):
        model_type = RoleModel

    repository_type = Repository
