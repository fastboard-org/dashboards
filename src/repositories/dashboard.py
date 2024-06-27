from models.dashboard import Dashboard
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
