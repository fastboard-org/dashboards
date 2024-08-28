from models.dashboard import Dashboard, PublishedDashboard
from typing import List, Optional
from bson import ObjectId
from schemas.dashboard import (
    DashboardUpdate,
)
from errors import CustomException, ERR_INTERNAL
from motor.motor_asyncio import AsyncIOMotorClient as Session


class DashboardRepository:
    session: Session = None

    async def create(self, dashboard: Dashboard) -> Dashboard:
        try:
            await dashboard.insert(session=self.session)
            return dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error creating dashboard: {str(e)}"
            )

    async def publish(self, dashboard_id, dashboard) -> Dashboard:
        try:
            published_dashboard = await PublishedDashboard.find_one(
                {"dashboard_id": dashboard_id}, session=self.session
            )
            if not published_dashboard:
                published_dashboard = PublishedDashboard(
                    dashboard_id=dashboard_id, dashboard=dashboard
                )
            else:
                published_dashboard.dashboard_id = dashboard_id
                published_dashboard.dashboard = dashboard

            await published_dashboard.save(session=self.session)

            return published_dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error publishing dashboard: {str(e)}"
            )

    async def get_published(self, dashboard_id: ObjectId) -> Optional[PublishedDashboard]:
        try:
            published_dashboard = await PublishedDashboard.find_one(
                {"dashboard_id": dashboard_id}, session=self.session
            )
            return published_dashboard.dashboard if published_dashboard else None
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching published dashboard: {str(e)}"
            )

    async def get_by_id(self, dashboard_id: ObjectId) -> Optional[Dashboard]:
        try:
            dashboard = await Dashboard.get(dashboard_id, session=self.session)
            return dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching dashboard: {str(e)}"
            )

    async def update(
        self, dashboard_id: ObjectId, dashboard_query: DashboardUpdate
    ) -> Optional[Dashboard]:
        try:
            dashboard = await Dashboard.get(dashboard_id, session=self.session)
            data = {}
            for attr in dashboard_query.model_fields_set:
                data[attr] = getattr(dashboard_query, attr)

            await dashboard.update({"$set": data}, session=self.session)
            return dashboard
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error updating dashboard: {str(e)}"
            )

    async def delete(self, dashboard_id: ObjectId) -> bool:
        try:
            dashboard = await Dashboard.get(dashboard_id, session=self.session)
            res = await dashboard.delete(session=self.session)
            return res.deleted_count > 0
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error deleting dashboard: {str(e)}"
            )

    async def get(self, filters: List) -> List[Dashboard]:
        try:
            dashboards_query = Dashboard.find(session=self.session)
            for filter in filters:
                dashboards_query.find(
                    {filter["name"]: {filter["operator"]: filter["value"]}}
                )
            return await dashboards_query.to_list()

        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching dashboards: {str(e)}"
            )
