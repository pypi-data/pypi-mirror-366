from typing import Annotated
from uuid import UUID

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from advanced_alchemy.extensions.litestar.providers import create_service_dependencies
from advanced_alchemy.filters import (
    FilterTypes,
)
from advanced_alchemy.service import OffsetPagination

from litestar import get
from litestar.controller import Controller
from litestar.dto import DTOConfig
from litestar.params import Dependency

from ..services import RoleService
from ..models import RoleModel



class RoleDTO(SQLAlchemyDTO[RoleModel]):
    config = DTOConfig(
        exclude={
            "users",
            "created_at",
            "updated_at",
            "permissions.0.created_at",
            "permissions.0.updated_at",
        },
        max_nested_depth=1,
    )


class RoleController(Controller):
    dependencies = create_service_dependencies(
        RoleService,
        key="roles_service",
        load=[RoleModel.permissions],
        filters={
            "id_filter": UUID,
            "created_at": True,
            "updated_at": True,
            "pagination_type": "limit_offset",
        },
    )

    return_dto = RoleDTO

    @get(operation_id="ListRoles", path="/roles")
    async def list_roles(
        self,
        roles_service: RoleService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[RoleModel]:
        results, total = await roles_service.list_and_count(*filters)
        return roles_service.to_schema(data=results, total=total, filters=filters)
