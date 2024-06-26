from models.folder import Folder
from models.dashboard import Dashboard
from typing import List, Optional
from bson import ObjectId
from schemas.folder import FolderUpdate, FoldersGet
from errors import CustomException, ERR_INTERNAL
from configs.database import mongodb as db
from schemas.folder import FolderResponse


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

    async def get_by_id(self, folder_id: ObjectId) -> Optional[FolderResponse]:
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "Dashboard",
                        "localField": "_id",
                        "foreignField": "folder_id",
                        "as": "dashboards",
                    }
                },
                {"$match": {"_id": folder_id}},
            ]
            folders = await Folder.aggregate(
                pipeline, projection_model=FolderResponse
            ).to_list()
            return folders[0] if folders else None
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
            async with db.start_transaction() as session:
                await Dashboard.find(Dashboard.folder_id == folder_id).update(
                    {"$set": {"folder_id": None}},
                    session=session,
                )
                await folder.delete(session=session)
            return True
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error deleting folder: {str(e)}",
            )

    async def get(self, folder_query: FoldersGet) -> List[Folder]:
        try:
            match_stage = {"$match": {}}

            if folder_query.user_id:
                match_stage["$match"]["user_id"] = folder_query.user_id
            if folder_query.name:
                match_stage["$match"]["name"] = folder_query.name

            pipeline = [
                {
                    "$lookup": {
                        "from": "Dashboard",
                        "localField": "_id",
                        "foreignField": "folder_id",
                        "as": "dashboards",
                    }
                },
                match_stage,
            ]

            folders = await Folder.aggregate(
                pipeline, projection_model=FolderResponse
            ).to_list()
            return folders
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error fetching folders: {str(e)}",
            )
