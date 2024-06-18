from models.dashboard import Dashboard
from typing import List, Optional
from bson import ObjectId
from schemas.dashboard import (
    DashboardUpdate,
    DashboardsGet,
)
from errors import CustomException, ERR_INTERNAL


class DashboardRepository:
    async def create(self, dashboard: Dashboard) -> Dashboard:
        try:
            await dashboard.insert()
            return dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error creating dashboard: {str(e)}"
            )

    async def get_by_id(self, dashboard_id: ObjectId) -> Optional[Dashboard]:
        try:
            dashboard = await Dashboard.get(dashboard_id)
            return dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching dashboard: {str(e)}"
            )

    async def update(
        self, dashboard_id: ObjectId, dashboard_query: DashboardUpdate
    ) -> Optional[Dashboard]:
        try:
            dashboard = await Dashboard.get(dashboard_id)
            data = {}
            for attr in dashboard_query.model_fields:
                data_attr = getattr(dashboard_query, attr)
                if data_attr:
                    data[attr] = data_attr

            await dashboard.update({"$set": data})
            return dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error updating dashboard: {str(e)}"
            )

    async def delete(self, dashboard_id: ObjectId) -> bool:
        try:
            dashboard = await Dashboard.get(dashboard_id)
            await dashboard.delete()
            return True
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error deleting dashboard: {str(e)}"
            )

    async def get(self, dashboard_query: DashboardsGet) -> List[Dashboard]:
        try:
            dashboards_query = Dashboard.find()

            if dashboard_query.user_id:
                dashboards_query = dashboards_query.find(
                    Dashboard.user_id == dashboard_query.user_id
                )
            if dashboard_query.name:
                dashboards_query = dashboards_query.find(
                    Dashboard.name == dashboard_query.name
                )
            if dashboard_query.folder_id:
                dashboards_query = dashboards_query.find(
                    Dashboard.folder_id == dashboard_query.folder_id
                )

            return await dashboards_query.to_list()
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching dashboards: {str(e)}"
            )
