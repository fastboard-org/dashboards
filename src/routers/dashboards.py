from fastapi import APIRouter, Depends
from typing import List
from repositories.dashboard import DashboardRepository
from services.dashboard import DashboardService
from beanie import PydanticObjectId as ObjectId
from schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardsGet,
)
from repositories.folder import FolderRepository


DashboardsRouter = APIRouter(prefix="/v1/dashboards", tags=["dashboards"])


def get_dashboard_service():
    dashboard_repository = DashboardRepository()
    folder_repository = FolderRepository()
    service = DashboardService(dashboard_repository, folder_repository)
    return service


@DashboardsRouter.post("/", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate, service: DashboardService = Depends(get_dashboard_service)
):
    return await service.create_dashboard(dashboard)


@DashboardsRouter.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: ObjectId, service: DashboardService = Depends(get_dashboard_service)
):
    return await service.get_dashboard_by_id(dashboard_id)


@DashboardsRouter.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: ObjectId,
    dashboard: DashboardUpdate,
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.update_dashboard(dashboard_id, dashboard)


@DashboardsRouter.delete("/{dashboard_id}", response_model=bool)
async def delete_dashboard(
    dashboard_id: ObjectId, service: DashboardService = Depends(get_dashboard_service)
):
    return await service.delete_dashboard(dashboard_id)


@DashboardsRouter.get("/", response_model=List[DashboardResponse])
async def list_dashboards(
    dashboards: DashboardsGet = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_dashboards(dashboards)
