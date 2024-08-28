from fastapi import APIRouter, Depends
from typing import List
from services.dashboard import DashboardService
from beanie import PydanticObjectId as ObjectId
from schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardsGet,
)
from repositories.registry import RepositoryRegistry
from configs.database import mongodb as db


DashboardsRouter = APIRouter(prefix="/v1/dashboards", tags=["dashboards"])


def get_dashboard_service():
    repository = RepositoryRegistry(db)
    service = DashboardService(repository)
    return service


@DashboardsRouter.post("/{dashboard_id}/published", response_model=DashboardResponse)
async def publish_dashboard(
    dashboard_id: ObjectId,
    user_id: str,
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.publish_dashboard(dashboard_id, user_id)


@DashboardsRouter.post("/", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate, service: DashboardService = Depends(get_dashboard_service)
):
    return await service.create_dashboard(dashboard)


@DashboardsRouter.get("/{dashboard_id}/published", response_model=DashboardResponse)
async def get_published_dashboard(
    dashboard_id: ObjectId,
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_published_dashboard(dashboard_id)


@DashboardsRouter.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: ObjectId,
    user_id: str,
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_dashboard_by_id(dashboard_id, user_id)


@DashboardsRouter.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: ObjectId,
    dashboard: DashboardUpdate,
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.update_dashboard(dashboard_id, dashboard)


@DashboardsRouter.delete("/{dashboard_id}", response_model=bool)
async def delete_dashboard(
    dashboard_id: ObjectId,
    user_id: str,
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.delete_dashboard(dashboard_id, user_id)


@DashboardsRouter.get("/", response_model=List[DashboardResponse])
async def list_dashboards(
    dashboards: DashboardsGet = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_dashboards(dashboards)
