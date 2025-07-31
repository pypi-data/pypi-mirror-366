from __future__ import annotations

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from ..models import PermissionModel

__all__ = ("PermissionService",)


class PermissionService(SQLAlchemyAsyncRepositoryService[PermissionModel]):
    class Repository(SQLAlchemyAsyncRepository[PermissionModel]):
        model_type = PermissionModel

    repository_type = Repository
