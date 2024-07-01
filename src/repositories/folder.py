from models.folder import Folder
from typing import List, Optional
from bson import ObjectId
from schemas.folder import FolderUpdate
from errors import CustomException, ERR_INTERNAL
from schemas.folder import FolderResponse
from motor.motor_asyncio import AsyncIOMotorClient as Session


class FolderRepository:
    session: Session = None

    async def create(self, folder: Folder) -> Folder:
        try:
            await folder.insert(session=self.session)
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
                pipeline, projection_model=FolderResponse, session=self.session
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
            folder = await Folder.get(folder_id, session=self.session)
            data = {}
            for attr in folder_query.model_fields_set:
                data[attr] = getattr(folder_query, attr)
            await folder.update({"$set": data}, session=self.session)
            return folder
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error updating folder: {str(e)}",
            )

    async def delete(self, folder_id: ObjectId) -> bool:
        try:
            folder = await Folder.get(folder_id, session=self.session)
            res = await folder.delete(session=self.session)
            return res.deleted_count > 0
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error deleting folder: {str(e)}",
            )

    async def get(self, filters: List) -> List[Folder]:
        try:
            match_stage = {"$match": {}}
            for filter in filters:
                match_stage["$match"][filter["name"]] = {
                    filter["operator"]: filter["value"]
                }
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
                pipeline, projection_model=FolderResponse, session=self.session
            ).to_list()
            return folders
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"Error fetching folders: {str(e)}",
            )
