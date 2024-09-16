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
    ERR_NOT_AUTHORIZED,
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
            if folder.user_id != dashboard_query.user_id:
                raise CustomException(
                    status_code=403,
                    error_code=ERR_NOT_AUTHORIZED,
                    description="You are not authorized to create a dashboard here",
                )

        dashboard = Dashboard(
            user_id=dashboard_query.user_id,
            name=dashboard_query.name,
            folder_id=dashboard_query.folder_id,
            metadata=dashboard_query.metadata,
        )
        return await self.repo.dashboard.create(dashboard)

    async def publish_dashboard(
        self, dashboard_id: ObjectId, user_id: str
    ) -> DashboardResponse:
        dashboard = await self.repo.dashboard.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        if dashboard.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to publish this dashboard",
            )
        await self.repo.dashboard.publish(dashboard_id, dashboard)
        return dashboard

    async def get_published_dashboard(
        self, dashboard_id: ObjectId
    ) -> Optional[DashboardResponse]:
        published_dashboard = await self.repo.dashboard.get_published(dashboard_id)
        if not published_dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find published dashboard with the given id",
            )
        return published_dashboard

    async def get_dashboard_by_id(
        self, dashboard_id: ObjectId, user_id: str
    ) -> Optional[DashboardResponse]:
        dashboard = await self.repo.dashboard.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        if dashboard.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to access this dashboard",
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
        if dashboard.user_id != dashboard_query.user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to update this dashboard",
            )
        if dashboard_query.folder_id:
            folder = await self.repo.folder.get_by_id(dashboard_query.folder_id)
            if not folder:
                raise CustomException(
                    status_code=404,
                    error_code=ERR_FOLDER_NOT_FOUND,
                    description="Could not find folder with the given id",
                )
            if folder.user_id != dashboard_query.user_id:
                raise CustomException(
                    status_code=403,
                    error_code=ERR_NOT_AUTHORIZED,
                    description="You are not authorized to move this dashboard here",
                )

        return await self.repo.dashboard.update(dashboard_id, dashboard_query)

    async def delete_dashboard(self, dashboard_id: ObjectId, user_id: str) -> bool:
        dashboard = await self.repo.dashboard.get_by_id(dashboard_id)
        if not dashboard:
            raise CustomException(
                status_code=404,
                error_code=ERR_DASHBOARD_NOT_FOUND,
                description="Could not find dashboard with the given id",
            )
        if dashboard.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to delete this dashboard",
            )

        async def delete_dashboard_transaction(repo_registry: RepositoryRegistry):
            published_dashboard = await repo_registry.dashboard.get_published(
                dashboard_id
            )
            if published_dashboard:
                await repo_registry.dashboard.unpublish(published_dashboard.id)
            return await repo_registry.dashboard.delete(dashboard_id)

        return await self.repo.transaction(delete_dashboard_transaction)

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
