from models.dashboard import Dashboard
from schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardsGet,
)
from typing import List, Optional
from beanie import PydanticObjectId as ObjectId
from errors import (
    CustomException,
    ERR_FOLDER_NOT_FOUND,
    ERR_DASHBOARD_NOT_FOUND,
)
from repositories.registry import RepositoryRegistry
from configs.database import Operators


class DashboardService:
    def __init__(
        self,
        repository: RepositoryRegistry,
    ):
        self.repo = repository

    async def create_dashboard(
        self, dashboard_query: DashboardCreate
    ) -> DashboardResponse:
        if dashboard_query.folder_id:
            folder = await self.repo.folder.get_by_id(dashboard_query.folder_id)
            if not folder:
                raise CustomException(
                    status_code=404,
                    error_code=ERR_FOLDER_NOT_FOUND,
                    description="Could not find folder with the given id",
                )

        dashboard = Dashboard(
            user_id=dashboard_query.user_id,
            name=dashboard_query.name,
            folder_id=dashboard_query.folder_id,
            metadata=dashboard_query.metadata,
        )
        return await self.repo.dashboard.create(dashboard)

    async def get_dashboard_by_id(
        self, dashboard_id: ObjectId
    ) -> Optional[DashboardResponse]:
        dashboard = await self.repo.dashboard.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        return dashboard

    async def update_dashboard(
        self, dashboard_id, dashboard_query: DashboardUpdate
    ) -> Optional[DashboardResponse]:
        dashboard = await self.repo.dashboard.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        if dashboard_query.folder_id:
            folder = await self.repo.folder.get_by_id(dashboard_query.folder_id)
            if not folder:
                raise CustomException(
                    status_code=404,
                    error_code=ERR_FOLDER_NOT_FOUND,
                    description="Could not find folder with the given id",
                )

        return await self.repo.dashboard.update(dashboard_id, dashboard_query)

    async def delete_dashboard(self, dashboard_id: ObjectId) -> bool:
        dashboard = await self.repo.dashboard.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        return await self.repo.dashboard.delete(dashboard_id)

    async def get_dashboards(
        self, dashboards_query: DashboardsGet
    ) -> List[DashboardResponse]:
        filters = []
        if dashboards_query.user_id:
            filters.append(
                {
                    "name": "user_id",
                    "value": dashboards_query.user_id,
                    "operator": Operators.EQ,
                }
            )
        if dashboards_query.name:
            filters.append(
                {"name": "name", "value": dashboards_query.name, "operator": Operators.EQ}
            )
        if dashboards_query.folder_id:
            filters.append(
                {
                    "name": "folder_id",
                    "value": dashboards_query.folder_id,
                    "operator": Operators.EQ,
                }
            )
        return await self.repo.dashboard.get(filters)
