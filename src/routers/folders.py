from fastapi import APIRouter, Depends
from typing import List
from services.folder import FolderService
from beanie import PydanticObjectId as ObjectId
from schemas.folder import FolderCreate, FolderUpdate, FolderResponse, FoldersGet
from repositories.registry import RepositoryRegistry
from configs.database import mongodb as db


FoldersRouter = APIRouter(prefix="/v1/folders", tags=["folders"])


def get_folder_service():
    repository = RepositoryRegistry(db)
    service = FolderService(repository)
    return service


@FoldersRouter.post("/", response_model=FolderResponse)
async def create_folder(
    folder: FolderCreate, service: FolderService = Depends(get_folder_service)
):
    return await service.create_folder(folder)


@FoldersRouter.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: ObjectId,
    user_id: str,
    service: FolderService = Depends(get_folder_service),
):
    return await service.get_folder_by_id(folder_id, user_id)


@FoldersRouter.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: ObjectId,
    folder: FolderUpdate,
    service: FolderService = Depends(get_folder_service),
):
    return await service.update_folder(folder_id, folder)


@FoldersRouter.delete("/{folder_id}", response_model=bool)
async def delete_folder(
    folder_id: ObjectId,
    user_id: str,
    service: FolderService = Depends(get_folder_service),
):
    return await service.delete_folder(folder_id, user_id)


@FoldersRouter.get("/", response_model=List[FolderResponse])
async def list_folders(
    folders: FoldersGet = Depends(), service: FolderService = Depends(get_folder_service)
):
    return await service.get_folders(folders)
