from models.dashboard import Dashboard
from typing import List, Optional
from bson import ObjectId
from schemas.dashboard import (
    DashboardUpdate,
    DashboardsGet,
)


class DashboardRepository:
    async def create(self, dashboard: Dashboard) -> Dashboard:
        await dashboard.insert()
        return dashboard

    async def get_by_id(self, dashboard_id: ObjectId) -> Optional[Dashboard]:
        return await Dashboard.get(dashboard_id)

    async def update(
        self, dashboard_id: ObjectId, dashboard_query: DashboardUpdate
    ) -> Optional[Dashboard]:
        dashboard = await Dashboard.get(dashboard_id)
        data = {}
        for attr in dashboard_query.model_fields:
            data[attr] = getattr(dashboard_query, attr)

        await dashboard.update({"$set": data})
        return dashboard
        return None

    async def delete(self, dashboard_id: ObjectId) -> bool:
        dashboard = await Dashboard.get(dashboard_id)
        if dashboard:
            await dashboard.delete()
            return True
        return False

    async def get(self, dashboard_query: DashboardsGet) -> List[Dashboard]:
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
