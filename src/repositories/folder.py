from models.folder import Folder
from models.dashboard import Dashboard
from typing import List, Optional
from bson import ObjectId
from schemas.folder import FolderUpdate, FoldersGet
from errors import CustomException, ERR_INTERNAL


class FolderRepository:
    async def create(self, folder: Folder) -> Folder:
        try:
            await folder.insert()
            return folder
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error creating folder: {str(e)}",
            )

    async def get_by_id(self, folder_id: ObjectId) -> Optional[Folder]:
        try:
            folder = await Folder.get(folder_id)
            return folder
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error fetching folder: {str(e)}",
            )

    async def update(
        self, folder_id: ObjectId, folder_query: FolderUpdate
    ) -> Optional[Folder]:
        try:
            folder = await Folder.get(folder_id)
            data = {}
            for attr in folder_query.model_fields_set:
                data[attr] = getattr(folder_query, attr)
            await folder.update({"$set": data})
            return folder
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error updating folder: {str(e)}",
            )

    async def delete(self, folder_id: ObjectId) -> bool:
        try:
            folder = await Folder.get(folder_id)
            # TODO: the deletion of the folder and the update of the
            # dashboards should bedone in a transaction
            await folder.delete()
            await Dashboard.find(Dashboard.folder_id == folder_id).update(
                {"$set": {"folder_id": None}}
            )
            return True
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error deleting folder: {str(e)}",
            )

    async def get(self, folder_query: FoldersGet) -> List[Folder]:
        try:
            folders_query = Folder.find()

            if folder_query.user_id:
                folders_query = folders_query.find(Folder.user_id == folder_query.user_id)
            if folder_query.name:
                folders_query = folders_query.find(Folder.name == folder_query.name)

            return await folders_query.to_list()
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error fetching folders: {str(e)}",
            )
