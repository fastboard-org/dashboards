from repositories.dashboard import DashboardRepository
from models.dashboard import Dashboard
from schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardsGet,
)
from typing import List, Optional
from bson import ObjectId
from repositories.folder import FolderRepository
from errors import CustomException, ERR_FOLDER_NOT_FOUND, ERR_DASHBOARD_NOT_FOUND


class DashboardService:
    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        folder_repository: FolderRepository,
    ):
        self.dashboard_repository = dashboard_repository
        self.folder_repository = folder_repository

    async def create_dashboard(
        self, dashboard_query: DashboardCreate
    ) -> DashboardResponse:
        if dashboard_query.folder_id:
            folder = await self.folder_repository.get_by_id(dashboard_query.folder_id)
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
        return await self.dashboard_repository.create(dashboard)

    async def get_dashboard_by_id(
        self, dashboard_id: ObjectId
    ) -> Optional[DashboardResponse]:
        dashboard = await self.dashboard_repository.get_by_id(dashboard_id)
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
        dashboard = await self.dashboard_repository.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        if dashboard_query.folder_id:
            folder = await self.folder_repository.get_by_id(dashboard_query.folder_id)
            if not folder:
                raise CustomException(
                    status_code=404,
                    error_code=ERR_FOLDER_NOT_FOUND,
                    description="Could not find folder with the given id",
                )
        return await self.dashboard_repository.update(dashboard_id, dashboard_query)

    async def delete_dashboard(self, dashboard_id: ObjectId) -> bool:
        dashboard = await self.dashboard_repository.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        return await self.dashboard_repository.delete(dashboard_id)

    async def get_dashboards(
        self, dashboards_query: DashboardsGet
    ) -> List[DashboardResponse]:
        return await self.dashboard_repository.get(dashboards_query)
