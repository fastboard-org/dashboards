from fastapi import APIRouter, Depends
from typing import List
from repositories.folder import FolderRepository
from services.folder import FolderService
from beanie import PydanticObjectId as ObjectId
from schemas.folder import FolderCreate, FolderUpdate, FolderResponse, FoldersGet
from repositories.dashboard import DashboardRepository
from errors import CustomException, ERR_FOLDER_NOT_FOUND


FoldersRouter = APIRouter(prefix="/v1/folders", tags=["folders"])


def get_folder_service():
    folder_repository = FolderRepository()
    dashboard_repository = DashboardRepository()
    service = FolderService(folder_repository, dashboard_repository)
    return service


@FoldersRouter.post("/", response_model=FolderResponse)
async def create_folder(
    folder: FolderCreate, service: FolderService = Depends(get_folder_service)
):
    return await service.create_folder(folder)


@FoldersRouter.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: ObjectId, service: FolderService = Depends(get_folder_service)
):
    folder = await service.get_folder_by_id(folder_id)
    if not folder:
        raise CustomException(
            status_code=404,
            error_code=ERR_FOLDER_NOT_FOUND,
            description="Could not find folder with the given id",
        )
    return folder


@FoldersRouter.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: ObjectId,
    folder: FolderUpdate,
    service: FolderService = Depends(get_folder_service),
):
    folder = await service.update_folder(folder_id, folder)
    return folder


@FoldersRouter.delete("/{folder_id}", response_model=bool)
async def delete_folder(
    folder_id: ObjectId, service: FolderService = Depends(get_folder_service)
):
    return await service.delete_folder(folder_id)


@FoldersRouter.get("/", response_model=List[FolderResponse])
async def list_folders(
    folders: FoldersGet = Depends(), service: FolderService = Depends(get_folder_service)
):
    return await service.get_folders(folders)
