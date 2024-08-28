from models.folder import Folder
from typing import List, Optional
from bson import ObjectId
from schemas.folder import FolderCreate, FolderUpdate, FolderResponse, FoldersGet
from errors import CustomException, ERR_FOLDER_NOT_FOUND, ERR_NOT_AUTHORIZED
from repositories.registry import RepositoryRegistry
from schemas.dashboard import DashboardUpdate
from configs.database import Operators


class FolderService:
    def __init__(
        self,
        repository: RepositoryRegistry,
    ):
        self.repo = repository

    async def create_folder(self, folder_query: FolderCreate) -> FolderResponse:
        folder = Folder(
            name=folder_query.name,
            user_id=folder_query.user_id,
        )
        created_folder = await self.repo.folder.create(folder)
        return FolderResponse(
            id=created_folder.id,
            name=created_folder.name,
            user_id=created_folder.user_id,
            dashboards=[],
        )

    async def get_folder_by_id(
        self, folder_id: ObjectId, user_id: str
    ) -> Optional[FolderResponse]:
        folder = await self.repo.folder.get_by_id(folder_id)
        if not folder:
            raise CustomException(
                status_code=404,
                error_code=ERR_FOLDER_NOT_FOUND,
                description="Could not find folder with the given id",
            )
        if folder.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to access this folder",
            )
        return folder

    async def update_folder(
        self, folder_id: ObjectId, folder_query: FolderUpdate
    ) -> Optional[FolderResponse]:
        folder = await self.repo.folder.get_by_id(folder_id)
        if not folder:
            raise CustomException(
                status_code=404,
                error_code=ERR_FOLDER_NOT_FOUND,
                description="Could not find folder with the given id",
            )
        if folder.user_id != folder_query.user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to update this folder",
            )

        updated_folder = await self.repo.folder.update(folder_id, folder_query)
        return FolderResponse(
            id=updated_folder.id,
            name=updated_folder.name,
            user_id=updated_folder.user_id,
            dashboards=folder.dashboards,
        )

    async def delete_folder(self, folder_id: ObjectId, user_id: str) -> bool:
        folder = await self.repo.folder.get_by_id(folder_id)
        if not folder:
            raise CustomException(
                status_code=404,
                error_code=ERR_FOLDER_NOT_FOUND,
                description="Could not find folder with the given id",
            )
        if folder.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to delete this folder",
            )

        async def delete_folder_transaction(repo_registry: RepositoryRegistry):
            dashboards = await repo_registry.dashboard.get(
                [{"name": "folder_id", "value": folder_id, "operator": Operators.EQ}]
            )
            for dashboard in dashboards:
                await repo_registry.dashboard.update(
                    dashboard.id, DashboardUpdate(folder_id=None)
                )
            return await repo_registry.folder.delete(folder_id)

        return await self.repo.transaction(delete_folder_transaction)

    async def get_folders(self, folder_query: FoldersGet) -> List[FolderResponse]:
        filters = []
        if folder_query.user_id:
            filters.append(
                {
                    "name": "user_id",
                    "value": folder_query.user_id,
                    "operator": Operators.EQ,
                }
            )
        if folder_query.name:
            filters.append(
                {
                    "name": "name",
                    "value": folder_query.name,
                    "operator": Operators.EQ,
                }
            )
        return await self.repo.folder.get(filters)
